#!/usr/bin/zsh

set -a; source ../.env; set +a

for f in "$CONTENT_DIR/artwork/png/*.png"; do
  base=$(basename "${f%.*}")
  out_file="$CONTENT_DIR/artwork/webp/$base.webp"
  if [[ ! -e "$out_file" ]]; then
    cwebp -q 80 "$f" -o "$out_file"
  fi
done