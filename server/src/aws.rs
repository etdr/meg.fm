

use aws_sdk_s3 as s3;



pub async fn get_track_materials() {

	let awsconfig = aws_config::load_from_env().await;
	let client = s3::Client::new(&awsconfig);

	client.list_objects_v2().bucket("meg.fm");
}