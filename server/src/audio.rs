
use std::fs::File;
use std::io::Read;
use std::error::Error;
// use futures::stream::Stream;
use opus::{Decoder, Channels};
use ogg::{PacketReader, Packet};


const TEST_OPUS_PATH: &'static str = "/home/winfield/projects/meg.fm/content/music/ab40037e-41c0-4b94-b349-93286ab6d014.opus";

pub fn load_and_decode() -> Result<Vec<i16>, Box<dyn std::error::Error>> {

	let file = File::open(TEST_OPUS_PATH)?;
	// let mut opus_data = Vec::new();
	// file.read_to_end(&mut opus_data)?;
	let mut pr = PacketReader::new(file);

	let mut decoder = Decoder::new(24000, Channels::Mono)?;
	let mut output_buffer: Vec<i16> = vec![0; 500];

	loop {
		match pr.read_packet() {
			Ok(Some(pkt)) => {
				let mut pcm = vec![0i16; 5760];
				if let Ok(samples) = decoder.decode(&pkt.data, &mut pcm, false) {
					output_buffer.extend_from_slice(&pcm[0..samples]);
				}
			}
			Ok(None) => {
				break;
			}
			Err(e) => {
				eprintln!("Error decoding: {:?}", e);
				break;
			}
		}
	}

	// while offset < opus_data.len() {
	// 	let packet_size = get_next_packet_size(&opus_data[offset..])?;

	// 	let packet_data = &opus_data[offset..(offset + packet_size)];

	// 	let mut decoded_buffer: Vec<i16> = vec![0; packet_size * 2];

	// 	match decoder.decode(packet_data, &mut decoded_buffer, false) {
	// 		Ok(samples) => {
	// 			output_buffer.extend_from_slice(&decoded_buffer[0..samples]);
	// 		},
	// 		Err(err) => {
	// 			eprintln!("Failed to decode packet: {:?}", err);
	// 		}
	// 	}

	

	// let output_slice = &mut decoded_buffer[..];
	// decoder.decode(&opus_data, output_slice, false)?;

	Ok(output_buffer)
}

// fn get_next_packet_size(data: &[u8]) -> Result<usize, Box<dyn Error>> {

// 	Ok(0)
// }


