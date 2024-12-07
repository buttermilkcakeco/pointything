import Alpine from 'alpinejs'

export interface RoomType {
  id: string
  revealed: boolean
  parcipants: {
    id: string
    name: string
    vote?: string
  }[]
}

export const joinRoom = async ({ roomId, userName }): Promise<string> => {
  try {
    const url = `/api/room/${roomId}/join`
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userName }),
    })
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`)
    }

    const json = await response.json()
    return json.user
  } catch (error) {
    console.error(error.message)
  }
}

let serverSocket: WebSocket

export const connectRoom = ({ roomId, userId }) => {
  Alpine.store('room').id = roomId
  Alpine.store('user').id = userId

  if (!roomId || !userId) {
    return
  }

  const prot = window.location.protocol === 'http:' ? 'ws:' : 'wss:'

  const socketUrl = `${prot}//${window.location.host}/api/ws/roomhub/${roomId}/${userId}`
  serverSocket = new WebSocket(socketUrl)

  serverSocket.onmessage = (ev) => {
    const { type, data } = JSON.parse(ev.data)
    console.log('RX', type, data)

    if (type === 'roomUpdate') {
      Alpine.store('room', data)
    }
  }

  serverSocket.onclose = () => {
    console.error('Socket closed unexpectedly')
  }
}

const _send = (type, data) => {
  console.log('TX', type, data)
  serverSocket.send(JSON.stringify({ type, data }))
}

export const vote = (points) => _send('vote', points)
export const unvote = () => _send('unvote', {})
export const resetVotes = () => _send('reset', {})
export const reveal = () => _send('reveal', {})
export const unreveal = () => _send('unreveal', {})
export const removeUser = (userId) => _send('removeUser', userId)

export const myVote = () => {
  const userId = Alpine.store('user').id
  return Alpine.store('room')?.participants?.find(({ id }) => id == userId)
    ?.vote
}

export const consensus = () => {
  const parts = Alpine.store('room')?.participants
  const votes = parts?.filter(({ vote }) => vote).map(({ vote }) => vote)
  return votes.length > 1 && votes.every(({ vote }) => vote == votes[0])
}
