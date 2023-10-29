
use std::env;
use axum::extract::Extension;
use axum::http::HeaderValue;
use hyper::{HeaderMap, StatusCode};
use base64::{Engine as _, engine::general_purpose as gp};

pub fn check_auth(headers: &HeaderMap<HeaderValue>) -> bool {
	let c_user = env::var("SERVER_USERNAME").unwrap_or_default();
	let c_pass = env::var("SERVER_PASSWORD").unwrap_or_default();

	match headers.get("Authorization") {
		Some(value) => {
			let auth_str = value.to_str().unwrap_or("");
			if auth_str.starts_with("Basic ") {
				let base64_enc = &auth_str[6..];
				let decoded = gp::STANDARD_NO_PAD.decode(base64_enc).unwrap_or_else(|_| Vec::new());
				let decoded_str = String::from_utf8_lossy(&decoded);
				let parts: Vec<&str> = decoded_str.split(":").collect();
				if parts.len() == 2 && parts[0] == c_user && parts[1] == c_pass {
					return true;
				}
			}
		},
		None => {}
	}
	false
}