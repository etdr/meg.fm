
use axum::{extract::Json, response::IntoResponse, Extension, http::HeaderValue};
use hyper::{StatusCode, HeaderMap};
use rusqlite::{params, Connection, Result};
use serde::Deserialize;

use crate::auth;


pub struct UuidList {
	uuids: Vec<String>,
}

const DB_PATH: &'static str = "/home/winfield/projects/meg.fm/code/server/db.db";

pub async fn update_db(
	Json(uuid_list): Json<UuidList>,
	Extension(headers): Extension<HeaderMap<HeaderValue>>)
	-> Result<impl IntoResponse, StatusCode> {

	if !auth::check_auth(&headers) {
		return Err(StatusCode::UNAUTHORIZED);
	}
	
	match update(&uuid_list.uuids) {
		Ok(_) => Ok((StatusCode::OK, "Database updated")),
		Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
	}
}

fn update(uuids: &[String]) -> Result<(), rusqlite::Error> {

	// let uuids = &uuid_list;
	// let uuid_params: Vec<&dyn rusqlite::ToSql> =
	// 	uuids.iter().map(|x| x as &dyn rusqlite::ToSql).collect();

	let conn = Connection::open(DB_PATH)?;

	conn.execute(
		"CREATE TABLE IF NOT EXISTS tracks (
			uuid TEXT PRIMARY KEY
		)", 
		[]
	)?;

	let params: Vec<String> = uuids.iter().map(|_| "?".to_string()).collect();
	// let stmt = format!(
	// 	"INSERT OR IGNORE INTO tracks (uuid) VALUES ({})",
	// 	params.join(", ")
	// );
	let mut stmt = conn.prepare(
		"INSERT OR IGNORE INTO tracks (uuid) VALUES (?)")?;

	for uuid in uuids {
		stmt.execute([uuid])?;
	}

	Ok(())
}