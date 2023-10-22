#!/usr/bin/zsh

set -a; source ../.env; set +a

aws s3 sync "$CONTENT_DIR/info"          s3://meg.fm/info
aws s3 sync "$CONTENT_DIR/music"         s3://meg.fm/music
aws s3 sync "$CONTENT_DIR/artwork/webp"  s3://meg.fm/artwork