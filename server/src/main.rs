
use std::{sync::Arc, time::Duration};

use audio::load_and_decode;
use bytes::Bytes;

use byteorder::{ByteOrder, LittleEndian};

use chrono::Local;

use sha2::{Sha256, Digest};

use axum::{
	routing::{get, post},
	Router,
	response::{IntoResponse, Response},
	extract::ws::{Message, WebSocket, WebSocketUpgrade},
	TypedHeader
};
use futures::{sink::SinkExt, stream::StreamExt, lock};
use hyper::Client;
use tokio::{sync::{broadcast, RwLock}, time::sleep};

use std::sync::Once;
use std::time::Instant;
use dotenv::dotenv;

mod audio;
mod aws;
mod update_db;
mod auth;

pub struct AudioTrack {
	packets: Vec<Vec<u8>>,
	packet_duration: u64,
	track_duration: u64,
}

struct GlobalAudioState {
	track_start_instant: Instant,
	current_track: AudioTrack,
}

impl GlobalAudioState {
	fn new() -> GlobalAudioState {
		GlobalAudioState {
			track_start_instant: Instant::now(),
			current_track: load_and_decode().unwrap()
		}
	}

	fn current_packet(&self) -> Option<&Vec<u8>> {
		let elapsed = self.track_start_instant.elapsed().as_millis() as u64;
		if elapsed >= self.current_track.track_duration {
			None
		} else {
			let packet_index = elapsed / self.current_track.packet_duration;
			self.current_track.packets.get(packet_index as usize)
		}
	}

	async fn load_next_track(&mut self) {
		self.current_track = load_and_decode().unwrap();
		self.track_start_instant = Instant::now();
	}

	fn should_load_next_track(&self) -> bool {
		let elapsed = self.track_start_instant.elapsed().as_millis() as u64;
		elapsed >= self.current_track.track_duration
	}
}



static INIT: Once = Once::new();


#[tokio::main]
async fn main() {

	INIT.call_once(|| {
		dotenv().ok();
	});	

	let global_audio_state = Arc::new(RwLock::new(GlobalAudioState::new()));

	let (tx, _rx) = broadcast::channel::<Vec<u8>>(200);
	// let tx_clone = tx.clone();

	let gas_dj_clone = Arc::clone(&global_audio_state);
	tokio::spawn(async {
		dj_loop(gas_dj_clone).await;
	});

	let gas_tx_clone = Arc::clone(&global_audio_state);
	let tx_sbl = tx.clone();
	tokio::spawn(async {
		server_broadcast_loop(gas_tx_clone, tx_sbl).await;
	});

	
	let tx_for_route = tx.clone();
	let app = Router::new()
		.route("/", get(|| async { "hello there" }))
		.route("/audio", get(|ws| ws_handler(ws, tx_for_route)));
		// .route("/updatedb", post(update_db::update_db));

	let addr = "0.0.0.0:30303".parse().unwrap();
	axum::Server::bind(&addr)
		.serve(app.into_make_service())
		.await
		.unwrap();

	
}

async fn ws_handler(ws: WebSocketUpgrade, tx: broadcast::Sender<Vec<u8>>) -> impl IntoResponse {
	ws.on_upgrade(move |socket| handle_websocket(socket, tx))
}


async fn handle_websocket(socket: WebSocket, tx: broadcast::Sender<Vec<u8>>) {

	// let locked_state = shared_audio_state.read().await;
	
	let (mut ws_tx, mut ws_rx) = socket.split();

	let mut rx = tx.subscribe();

	tokio::spawn(async move {
		while let Some(result) = ws_rx.next().await {
			match result {
				Ok(msg) => {
					println!("{}", msg.to_text().unwrap());
				},
				Err(e) => {
					panic!("{}", e);
				}
			}
		}
	});

	while let Ok(audio_chunk) = rx.recv().await {
		// println!("sending chunk");
		if let Err(_) = ws_tx.send(Message::Binary(audio_chunk)).await {
			break;
		}
	}
}


async fn server_broadcast_loop(state: Arc<RwLock<GlobalAudioState>>, tx: broadcast::Sender<Vec<u8>>) {
	loop {
		let audio_packet;
		{
			let read_state = state.read().await;
			audio_packet = read_state.current_packet().cloned();
		}

		if let Some(packet) = audio_packet {
			if let Err(e) = tx.send(packet) {
				eprintln!("Error broadcasting packet: {:?}", e);
			} else {
				// println!("Sent packet");
			}
		} else {
			eprintln!("No packet to broadcast");
		}

		tokio::time::sleep(Duration::from_millis(20)).await;
	}
}

async fn dj_loop(state: Arc<RwLock<GlobalAudioState>>) {
	loop {
		{
			let read_state = state.read().await;
			if read_state.should_load_next_track() {
				println!("switching track");
				drop(read_state);

				let mut write_state = state.write().await;
				write_state.load_next_track().await;
			}
		}

		sleep(Duration::from_millis(100)).await;
	}
}