import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import KPICard from '../components/KPICard'

describe('KPICard', () => {
  it('renders label and value', () => {
    render(<KPICard label="Composite Score" value={72} />)
    expect(screen.getByText('Composite Score')).toBeInTheDocument()
    expect(screen.getByText('72')).toBeInTheDocument()
  })

  it('renders subtitle when provided', () => {
    render(<KPICard label="Score" value={85} subtitle="Target: 80" />)
    expect(screen.getByText('Target: 80')).toBeInTheDocument()
  })

  it('renders risk badge when risk prop is provided', () => {
    render(<KPICard label="Risk" value="High" risk="HIGH" />)
    expect(screen.getByText('HIGH Risk')).toBeInTheDocument()
  })

  it('applies green color for LOW risk', () => {
    render(<KPICard label="Test" value={90} risk="LOW" />)
    const card = screen.getByText('Test').closest('div')
    expect(card.className).toContain('green')
  })

  it('applies red color for HIGH risk', () => {
    render(<KPICard label="Test" value={30} risk="HIGH" />)
    const card = screen.getByText('Test').closest('div')
    expect(card.className).toContain('red')
  })
})
