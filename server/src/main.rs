
use std::sync::Arc;

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
use tokio::sync::{broadcast, RwLock};

use std::sync::Once;
use dotenv::dotenv;

mod audio;
mod aws;
mod update_db;
mod auth;

type AudioTrack = Vec<i16>;

struct GlobalAudioState {
	playhead: usize,
	current_track: AudioTrack,
	audio_slice: Vec<u8>,
}

static INIT: Once = Once::new();


#[tokio::main]
async fn main() {

	INIT.call_once(|| {
		dotenv().ok();
	});	

	let global_audio_state = Arc::new(RwLock::new(GlobalAudioState {
		playhead: 0,
		current_track: audio::load_and_decode().unwrap(),
		audio_slice: Vec::new(),
	}));

	let (tx, _rx) = broadcast::channel(200);
	let tx_clone = tx.clone();

	tokio::spawn(async move {
		let global_audio_state = Arc::clone(&global_audio_state);

		loop {
			let mut locked_state = global_audio_state.write().await;

			if should_swap_track(locked_state.playhead, &locked_state.current_track) {
				locked_state.current_track = audio::load_and_decode().unwrap();
				locked_state.playhead = 0;
			}

			let mut next_position = locked_state.playhead + (24000 as f32 * 1000 as f32 / 1000.0) as usize;
			if next_position > locked_state.current_track.len() {
				next_position = locked_state.current_track.len();
			}

			let audio_slice = &locked_state.current_track[locked_state.playhead..next_position];

			let mut byte_buffer = vec![0u8; audio_slice.len() * 2];
			LittleEndian::write_i16_into(audio_slice, &mut byte_buffer);
			// let audio_chunk = Bytes::copy_from_slice(&byte_buffer);

			let mut hasher = Sha256::new();
			hasher.update(&byte_buffer);
			let hash_result = hasher.finalize();
			locked_state.audio_slice = byte_buffer;

			println!("broadcasting chunk {:x} at {}", hash_result, Local::now().format("%H:%M:%S%.3f"));
			if let Err(e) = tx_clone.send(locked_state.audio_slice.clone()) {
				panic!("{}", e);
			}

			locked_state.playhead = next_position;

			tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
		}
	});
	
	let tx_for_route = tx.clone();
	let app = Router::new()
		.route("/", get(|| async { "hello there" }))
		.route("/audio", get(|ws| ws_handler(ws, tx_for_route)))
		.route("/updatedb", post(update_db::update_db));

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
		println!("sending chunk");
		if let Err(_) = ws_tx.send(Message::Binary(audio_chunk)).await {
			break;
		}
	}
}

fn should_swap_track(playhead: usize, current_track: &AudioTrack) -> bool {
	if playhead >= 60 * 24000 {
		return true;
	}
	false
}