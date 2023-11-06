
import aPFile from '$lib/audioProcessor.js?raw'

export function GET({ url }) {
	return new Response(aPFile, {
		headers: {
			'Content-Type': 'application/javascript'
		}
	})
}