import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'

export default defineConfig({
	plugins: [sveltekit()],
	css: {
		transformer: 'lightningcss',
		lightningcss: {
			drafts: {
				'customMedia': true
			}
		}
	}
})
