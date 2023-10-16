<script>

  import { io } from 'socket.io-client'

  const socket = io('http://localhost:5000')

  socket.on('connect', () => console.log('connected to websocket'))

  let title = ''

  function changeTitle (newtitle) {
    title = newtitle
  }

  socket.on('changetitle', changeTitle)
</script>

<h1>{title}</h1>