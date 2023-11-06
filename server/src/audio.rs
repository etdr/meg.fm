
use std::fs::File;
use std::io::Read;
use std::error::Error;
// use futures::stream::Stream;
use opus::{Decoder, Channels};
use ogg::{PacketReader, Packet};

use crate::AudioTrack;


const TEST_OPUS_PATH: &'static str = "/home/winfield/projects/meg.fm/content/music/ab40037e-41c0-4b94-b349-93286ab6d014.opus";

pub fn load_and_decode() -> Result<AudioTrack, Box<dyn std::error::Error>> {

	let file = File::open(TEST_OPUS_PATH)?;
	
	let mut pr = PacketReader::new(file);

	let mut opus_packets: Vec<Vec<u8>> = Vec::new();

	while let Ok(Some(packet)) = pr.read_packet() {
		let aligned_packet = ensure_mult_of_4(packet.data);
		opus_packets.push(aligned_packet);
	}

	// let mut decoder = Decoder::new(24000, Channels::Mono)?;
	// let mut output_buffer: Vec<i16> = vec![0; 500];

	// loop {
	// 	match pr.read_packet() {
	// 		Ok(Some(pkt)) => {
	// 			let mut pcm = vec![0i16; 5760];
	// 			if let Ok(samples) = decoder.decode(&pkt.data, &mut pcm, false) {
	// 				output_buffer.extend_from_slice(&pcm[0..samples]);
	// 			}
	// 		}
	// 		Ok(None) => {
	// 			break;
	// 		}
	// 		Err(e) => {
	// 			eprintln!("Error decoding: {:?}", e);
	// 			break;
	// 		}
	// 	}
	// }

	Ok(AudioTrack { packets: opus_packets, packet_duration: 20, track_duration: 60000 })
}

// fn get_next_packet_size(data: &[u8]) -> Result<usize, Box<dyn Error>> {

// 	Ok(0)
// }


fn ensure_mult_of_4(mut packet: Vec<u8>) -> Vec<u8> {
	let extra_bytes = packet.len() % 4;
	if extra_bytes != 0 {
		packet.extend(vec![0; 4 - extra_bytes]);
	}
	packet
}
