
use axum::{
	routing::get,
	Router
};

// THIS IS THE DEMO APP. I AM LEARNING

#[tokio::main]
async fn main() {
	
	let app = Router::new()
		.route("/", get(|| async { "hello there" }));

	let addr = "0.0.0.0:30303".parse().unwrap();
	axum::Server::bind(&addr)
		.serve(app.into_make_service())
		.await
		.unwrap();
}

