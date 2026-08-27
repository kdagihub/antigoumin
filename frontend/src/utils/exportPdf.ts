export interface PdfLine {
  label: string
  value: string
}

export interface AntiGouminPdfOptions {
  service: string
  title: string
  lines: PdfLine[]
  disclaimer?: string
  filename: string
}

const DEFAULT_DISCLAIMER =
  'Ce document atteste uniquement d’une consultation AntiGoumin à la date indiquée. ' +
  'Il ne constitue pas une preuve juridique et ne reflète que les données certifiées ' +
  'disponibles sur la plateforme au moment de la consultation.'

const WIN_ANSI: Record<string, number> = {
  '€': 128,
  '‚': 130,
  'ƒ': 131,
  '„': 132,
  '…': 133,
  '†': 134,
  '‡': 135,
  'ˆ': 136,
  '‰': 137,
  'Š': 138,
  '‹': 139,
  'Œ': 140,
  'Ž': 142,
  '‘': 145,
  '’': 146,
  '“': 147,
  '”': 148,
  '•': 149,
  '–': 150,
  '—': 151,
  '˜': 152,
  '™': 153,
  'š': 154,
  '›': 155,
  'œ': 156,
  'ž': 158,
  'Ÿ': 159,
  ' ': 32,
  '!': 33,
  '"': 34,
  '#': 35,
  $: 36,
  '%': 37,
  '&': 38,
  "'": 39,
  '(': 40,
  ')': 41,
  '*': 42,
  '+': 43,
  ',': 44,
  '-': 45,
  '.': 46,
  '/': 47,
  '0': 48,
  '1': 49,
  '2': 50,
  '3': 51,
  '4': 52,
  '5': 53,
  '6': 54,
  '7': 55,
  '8': 56,
  '9': 57,
  ':': 58,
  ';': 59,
  '<': 60,
  '=': 61,
  '>': 62,
  '?': 63,
  '@': 64,
  A: 65,
  B: 66,
  C: 67,
  D: 68,
  E: 69,
  F: 70,
  G: 71,
  H: 72,
  I: 73,
  J: 74,
  K: 75,
  L: 76,
  M: 77,
  N: 78,
  O: 79,
  P: 80,
  Q: 81,
  R: 82,
  S: 83,
  T: 84,
  U: 85,
  V: 86,
  W: 87,
  X: 88,
  Y: 89,
  Z: 90,
  '[': 91,
  '\\': 92,
  ']': 93,
  '^': 94,
  _: 95,
  '`': 96,
  a: 97,
  b: 98,
  c: 99,
  d: 100,
  e: 101,
  f: 102,
  g: 103,
  h: 104,
  i: 105,
  j: 106,
  k: 107,
  l: 108,
  m: 109,
  n: 110,
  o: 111,
  p: 112,
  q: 113,
  r: 114,
  s: 115,
  t: 116,
  u: 117,
  v: 118,
  w: 119,
  x: 120,
  y: 121,
  z: 122,
  '{': 123,
  '|': 124,
  '}': 125,
  '~': 126,
  '¡': 161,
  '¢': 162,
  '£': 163,
  '¤': 164,
  '¥': 165,
  '¦': 166,
  '§': 167,
  '¨': 168,
  '©': 169,
  'ª': 170,
  '«': 171,
  '¬': 172,
  '®': 174,
  '¯': 175,
  '°': 176,
  '±': 177,
  '²': 178,
  '³': 179,
  '´': 180,
  'µ': 181,
  '¶': 182,
  '·': 183,
  '¸': 184,
  '¹': 185,
  'º': 186,
  '»': 187,
  '¼': 188,
  '½': 189,
  '¾': 190,
  '¿': 191,
  'À': 192,
  'Á': 193,
  'Â': 194,
  'Ã': 195,
  'Ä': 196,
  'Å': 197,
  'Æ': 198,
  'Ç': 199,
  'È': 200,
  'É': 201,
  'Ê': 202,
  'Ë': 203,
  'Ì': 204,
  'Í': 205,
  'Î': 206,
  'Ï': 207,
  'Ð': 208,
  'Ñ': 209,
  'Ò': 210,
  'Ó': 211,
  'Ô': 212,
  'Õ': 213,
  'Ö': 214,
  '×': 215,
  'Ø': 216,
  'Ù': 217,
  'Ú': 218,
  'Û': 219,
  'Ü': 220,
  'Ý': 221,
  'Þ': 222,
  'ß': 223,
  'à': 224,
  'á': 225,
  'â': 226,
  'ã': 227,
  'ä': 228,
  'å': 229,
  'æ': 230,
  'ç': 231,
  'è': 232,
  'é': 233,
  'ê': 234,
  'ë': 235,
  'ì': 236,
  'í': 237,
  'î': 238,
  'ï': 239,
  'ð': 240,
  'ñ': 241,
  'ò': 242,
  'ó': 243,
  'ô': 244,
  'õ': 245,
  'ö': 246,
  '÷': 247,
  'ø': 248,
  'ù': 249,
  'ú': 250,
  'û': 251,
  'ü': 252,
  'ý': 253,
  'þ': 254,
  'ÿ': 255,
}

function encodePdfText(text: string): string {
  let encoded = ''
  for (const char of text.normalize('NFC')) {
    const code = WIN_ANSI[char]
    if (code === undefined) {
      encoded += '?'
      continue
    }
    if (code === 40 || code === 41 || code === 92) {
      encoded += `\\${String.fromCharCode(code)}`
    } else if (code < 32 || code > 126) {
      encoded += `\\${code.toString(8).padStart(3, '0')}`
    } else {
      encoded += String.fromCharCode(code)
    }
  }
  return encoded
}

function wrapText(text: string, maxChars: number): string[] {
  const words = text.split(/\s+/)
  const lines: string[] = []
  let current = ''
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word
    if (candidate.length > maxChars && current) {
      lines.push(current)
      current = word
    } else {
      current = candidate
    }
  }
  if (current) lines.push(current)
  return lines.length ? lines : ['']
}

function buildPdfContent(options: AntiGouminPdfOptions): string {
  const commands: string[] = []
  let y = 800

  const addText = (text: string, size: number, x: number, lineHeight: number) => {
    for (const line of wrapText(text, size >= 14 ? 60 : 78)) {
      commands.push('BT', `/F1 ${size} Tf`, `${x} ${y} Td`, `(${encodePdfText(line)}) Tj`, 'ET')
      y -= lineHeight
    }
  }

  addText('AntiGoumin', 18, 56, 24)
  addText(options.service, 11, 56, 18)
  y -= 6
  addText(options.title, 14, 56, 20)

  for (const line of options.lines) {
    y -= 4
    addText(`${line.label} : ${line.value}`, 11, 56, 16)
  }

  y -= 8
  const disclaimer = options.disclaimer ?? DEFAULT_DISCLAIMER
  for (const line of wrapText(disclaimer, 95)) {
    commands.push('BT', '/F1 9 Tf', `56 ${y} Td`, `(${encodePdfText(line)}) Tj`, 'ET')
    y -= 12
  }

  return commands.join('\n')
}

function createPdfBlob(options: AntiGouminPdfOptions): Blob {
  const stream = buildPdfContent(options)
  const objects = [
    '1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n',
    '2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n',
    '3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n',
    `4 0 obj\n<< /Length ${stream.length} >>\nstream\n${stream}\nendstream\nendobj\n`,
    '5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n',
  ]

  let pdf = '%PDF-1.4\n'
  const offsets: number[] = [0]

  for (const object of objects) {
    offsets.push(pdf.length)
    pdf += object
  }

  const xrefOffset = pdf.length
  pdf += `xref\n0 ${objects.length + 1}\n`
  pdf += '0000000000 65535 f \n'
  for (let index = 1; index <= objects.length; index += 1) {
    pdf += `${String(offsets[index]).padStart(10, '0')} 00000 n \n`
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\n`
  pdf += `startxref\n${xrefOffset}\n%%EOF`

  return new Blob([pdf], { type: 'application/pdf' })
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename.endsWith('.pdf') ? filename : `${filename}.pdf`
  link.click()
  URL.revokeObjectURL(url)
}

export async function downloadAntiGouminPdf(options: AntiGouminPdfOptions): Promise<void> {
  const blob = createPdfBlob(options)
  triggerDownload(blob, options.filename)
}

export function formatPdfDate(value: string | Date): string {
  const date = typeof value === 'string' ? new Date(value) : value
  return date.toLocaleString('fr-CI', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
