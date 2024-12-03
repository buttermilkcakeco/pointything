import * as room from './room'
export { room }

export const copyText = (ev: MouseEvent, text: string) => {
  navigator.clipboard.writeText(text)
  if (ev.target instanceof HTMLButtonElement) {
    const check = document.createElement('span')
    check.className = 'iconify mdi--check'

    ev.target.appendChild(check)
    ev.target.setAttribute('disabled', 'disabled')
    setTimeout(() => {
      ;(ev.target as HTMLElement).removeChild(check)
      ;(ev.target as HTMLElement).removeAttribute('disabled')
    }, 2000)
  }
}
