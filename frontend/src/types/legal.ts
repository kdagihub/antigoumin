export interface LegalSection {
  id: string
  title: string
  paragraphs?: string[]
  list?: string[]
  subsections?: LegalSubsection[]
}

export interface LegalSubsection {
  id: string
  title: string
  paragraphs?: string[]
  list?: string[]
}

export interface LegalDocument {
  title: string
  subtitle: string
  lastUpdated: string
  preamble: string
  sections: LegalSection[]
}
