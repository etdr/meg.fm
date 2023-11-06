<script>
	import { onMount } from 'svelte'
	import { OpusDecoder } from 'opus-decoder'

	let audioContext = null
	// let source
	// let bufferLength
	// let dataArray

	const decoder = new OpusDecoder({
		forceStereo: true,
		sampleRate: 24000
	})

	async function setupAudioContext () {
		console.log('setting up audio context')
		// audioContext = new (window.AudioContext || window.webkitAudioContext)()
		audioContext = new window.AudioContext({
			sampleRate: 24000
		})

		try {
			// await audioContext.resume()
			await audioContext.audioWorklet.addModule('/api/audio')
		} catch (e) {
			console.error(e)
		}

		console.log(audioContext)

		const aWN = new AudioWorkletNode(audioContext, 'meg-audio-processor', {
			outputChannelCount: [2]
		})

		aWN.connect(audioContext.destination)

		return aWN
	}

	async function setupStream () {
		try {
			
			const aWN = await setupAudioContext()


			const ws = new WebSocket('ws://localhost:30303/audio')
			ws.binaryType = 'arraybuffer'

			ws.onmessage = async (ev) => {
				// const aData = new Float32Array(ev.data)
				const aData = ev.data
				const opusPacket = new Uint8Array(aData)
				// const audioBuffer = await audioContext.decodeAudioData(aData)
				const { channelData } = decoder.decodeFrame(opusPacket)
				// console.log(channelData)

				aWN.port.postMessage(channelData)
			}
			

		} catch (e) {
			console.error(e)
		}
	}

	onMount(async () => {
		await decoder.ready
		setupStream()
	})

	let playing = false

	async function resumePlay () {
		playing = true
		let result = await audioContext.resume()
		console.log(result)
	}

	async function pausePlay () {
		playing = false
		let result = await audioContext.pausePlay()
	}
</script>


<slot />

<button on:click={resumePlay}>Play</button>