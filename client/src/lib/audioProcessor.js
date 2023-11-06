
class MegAudioProcessor extends AudioWorkletProcessor {
	constructor () {
		super()
		this.queue = []
		this.port.onmessage = this.handleMessage.bind(this)
	}

	handleMessage (data) {
		console.log('pushed data to queue')
		this.queue.push(data)
	}

	process(inputs, outputs, parameters) {
		const channels = outputs[0]
		if (this.queue.length) {
			const aD = this.queue.shift()
			if (!aD.length) return true
			for (let i = 0; i < channels[0].length; i++) {
				console.log('loading data')
				channels[0][i] = aD[0][i] ?? 0
				channels[1][i] = aD[1][i] ?? 0
			}
		} else {
			for (let i = 0; i < channels[0].length; i++) {
				console.log('loading zeroes')
				channels[0][i] = 0
				channels[1][i] = 0
			}
		}
		return true
	}
}

registerProcessor('meg-audio-processor', MegAudioProcessor)