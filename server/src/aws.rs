
use std::sync::Once;
use dotenv::dotenv;

static INIT: Once = Once::new();

pub fn get_track_materials() {
	INIT.call_once(|| {
		dotenv().ok();
	})
}