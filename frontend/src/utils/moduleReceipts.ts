import type { Alliance } from '@/api/alliances'
import type { Declaration } from '@/api/declarations'
import type { VerificationHistoryItem } from '@/api/search'
import type { CertifiedStatus, SearchResult } from '@/api/search'
import type { TransparencyRequest } from '@/api/transparency'
import { verificationResultCopy } from '@/content/verificationResults'

import { downloadAntiGouminPdf, formatPdfDate, type PdfLine } from './exportPdf'

const declarationStatusLabels: Record<Declaration['status'], string> = {
  PENDING: 'En attente du partenaire',
  VERIFIED: 'Relation certifiée',
  REJECTED: 'Refusée',
  ENDED: 'Terminée',
}

const transparencyStatusLabels: Record<TransparencyRequest['status'], string> = {
  PENDING: 'En attente de réponse',
  ACCEPTED: 'Réponse reçue',
  REFUSED: 'Refusée',
  EXPIRED: 'Expirée',
  BLOCKED: 'Bloquée',
  REPORTED: 'Signalée',
}

const allianceStatusLabels: Record<Alliance['status'], string> = {
  PENDING_PARTNER: 'En attente du partenaire',
  ACTIVE: 'Alliance active',
  REFUSED: 'Refusée',
  ENDED: 'Terminée',
}

const declaredStatusLabels: Record<string, string> = {
  ENGAGED: 'En couple',
  AVAILABLE: 'Disponible',
  PREFER_NOT_TO_ANSWER: 'Préfère ne pas répondre',
}

function verificationTitle(status: CertifiedStatus): string {
  if (status === 'PAYMENT_REQUIRED') return 'Paiement requis'
  return verificationResultCopy[status].title
}

function verificationBody(status: CertifiedStatus): string {
  if (status === 'PAYMENT_REQUIRED') return ''
  return verificationResultCopy[status].body
}

export async function downloadVerificationResultPdf(
  result: SearchResult,
  consultedAt = new Date(),
): Promise<void> {
  if (result.certified_status === 'PAYMENT_REQUIRED') return
  const status = result.certified_status
  await downloadAntiGouminPdf({
    service: 'Vérification de statut',
    title: verificationTitle(status),
    filename: `antigoumin-verification-${result.phone.replace(/\D/g, '')}.pdf`,
    lines: [
      { label: 'Numéro', value: result.phone },
      { label: 'Résultat', value: verificationTitle(status) },
      { label: 'Détail', value: verificationBody(status) },
      { label: 'Montant', value: `${result.price_fcfa} FCFA` },
      { label: 'Consulté le', value: formatPdfDate(consultedAt) },
    ],
  })
}

export async function downloadVerificationHistoryPdf(item: VerificationHistoryItem): Promise<void> {
  const status = item.certified_status as Exclude<CertifiedStatus, 'PAYMENT_REQUIRED'>
  await downloadAntiGouminPdf({
    service: 'Vérification de statut',
    title: verificationTitle(status),
    filename: `antigoumin-verification-${item.phone.replace(/\D/g, '')}-${item.id}.pdf`,
    lines: [
      { label: 'Numéro', value: item.phone },
      { label: 'Résultat', value: verificationTitle(status) },
      { label: 'Détail', value: verificationBody(status) },
      { label: 'Montant', value: `${item.amount_fcfa} FCFA` },
      { label: 'Consulté le', value: formatPdfDate(item.consulted_at) },
    ],
  })
}

export async function downloadDeclarationPdf(item: Declaration): Promise<void> {
  const lines: PdfLine[] = [
    { label: 'Partenaire', value: item.partner_name },
    { label: 'Téléphone', value: item.partner_phone },
    { label: 'Statut', value: declarationStatusLabels[item.status] },
    { label: 'Relation', value: item.relation_type },
    {
      label: 'Visibilité',
      value: item.visibility === 'PUBLIC_CERTIFIED' ? 'Certifiée publique' : 'Privée',
    },
    { label: 'Créée le', value: formatPdfDate(item.created_at) },
  ]
  await downloadAntiGouminPdf({
    service: 'Déclaration de relation',
    title: `Déclaration — ${item.partner_name}`,
    filename: `antigoumin-declaration-${item.id}.pdf`,
    lines,
  })
}

export async function downloadTransparencyPdf(item: TransparencyRequest): Promise<void> {
  const lines: PdfLine[] = [
    { label: 'Numéro invité', value: item.target_phone },
    { label: 'Statut', value: transparencyStatusLabels[item.status] ?? item.status },
    { label: 'Envoyée le', value: formatPdfDate(item.created_at) },
    { label: 'Expire le', value: formatPdfDate(item.expires_at) },
  ]
  if (item.status === 'ACCEPTED' && item.declared_status) {
    lines.splice(2, 0, {
      label: 'Réponse privée',
      value:
        (declaredStatusLabels[item.declared_status] ?? item.declared_status) +
        (item.declared_partner_name ? ` (${item.declared_partner_name})` : ''),
    })
  }
  await downloadAntiGouminPdf({
    service: 'Demande de transparence',
    title: `Transparence — ${item.target_phone}`,
    filename: `antigoumin-transparence-${item.id}.pdf`,
    lines,
  })
}

export async function downloadAlliancePdf(
  item: Alliance,
  partnerName: string,
): Promise<void> {
  const lines: PdfLine[] = [
    { label: 'Partenaire', value: partnerName },
    { label: 'Statut', value: allianceStatusLabels[item.status] },
    { label: 'Créée le', value: formatPdfDate(item.created_at) },
  ]
  if (item.subscription_end_date) {
    lines.push({
      label: 'Abonnement jusqu’au',
      value: formatPdfDate(item.subscription_end_date),
    })
  }
  await downloadAntiGouminPdf({
    service: 'Alliance Digitale VIP',
    title: `Alliance — ${partnerName}`,
    filename: `antigoumin-alliance-${item.id}.pdf`,
    lines,
  })
}

export function verificationHistoryLabel(status: string): string {
  if (status === 'PAYMENT_REQUIRED') return 'Paiement requis'
  if (status in verificationResultCopy) {
    return verificationResultCopy[status as keyof typeof verificationResultCopy].title
  }
  return status
}
