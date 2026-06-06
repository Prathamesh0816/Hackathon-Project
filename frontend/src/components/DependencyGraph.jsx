import { useState, useEffect, useRef, useCallback } from 'react'

const COLORS = {
  High: '#dc2626',
  Medium: '#d97706',
  Low: '#16a34a',
  Critical: '#7c3aed',
}

export default function DependencyGraph({ employees, dependencies, onNodeClick, width = 700, height = 500 }) {
  const canvasRef = useRef(null)
  const animRef = useRef(null)
  const nodesRef = useRef([])
  const edgesRef = useRef([])
  const [hovered, setHovered] = useState(null)
  const [selected, setSelected] = useState(null)

  // Build graph when data changes
  useEffect(() => {
    if (!employees?.length) return

    const empMap = {}
    employees.forEach((e, i) => {
      empMap[e.employee] = {
        id: e.employee,
        label: e.employee,
        team: e.team,
        criticality: e.criticality || 'Medium',
        severity: e.severity_level || e.risk_level || 'Medium',
        isSpof: e.backup_available === 'No' || e.is_spof,
        dependentsCount: e.dependents_count || 0,
        x: Math.random() * width * 0.8 + width * 0.1,
        y: Math.random() * height * 0.8 + height * 0.1,
        vx: 0, vy: 0,
        radius: 20 + (e.dependents_count || 0) * 4,
      }
    })

    const edges = []
    const empNames = new Set(Object.keys(empMap))

    ;(dependencies || []).forEach((d) => {
      const src = d.owner || d.Dependent
      const tgt = d.dependent || d.Dependent
      if (empNames.has(src) && empNames.has(tgt) && src !== tgt) {
        const existingEdge = edges.find(
          (e) =>
            (e.source === src && e.target === tgt) || (e.source === tgt && e.target === src)
        )
        if (!existingEdge) {
          edges.push({ source: src, target: tgt, type: d.dependency_type || d.DependencyType || 'dependency' })
        }
      }
    })

    nodesRef.current = Object.values(empMap)
    edgesRef.current = edges

    // Force simulation
    let running = true
    const W = width, H = height
    const centerX = W / 2, centerY = H / 2

    function tick() {
      if (!running) return
      const nodes = nodesRef.current
      const edges = edgesRef.current

      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j]
          let dx = b.x - a.x, dy = b.y - a.y
          let dist = Math.sqrt(dx * dx + dy * dy) || 1
          const force = 5000 / (dist * dist)
          const fx = dx / dist * force
          const fy = dy / dist * force
          a.vx -= fx; a.vy -= fy
          b.vx += fx; b.vy += fy
        }
      }

      // Attraction along edges
      for (const edge of edges) {
        const a = nodes.find((n) => n.id === edge.source)
        const b = nodes.find((n) => n.id === edge.target)
        if (!a || !b) continue
        const dx = b.x - a.x, dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = dist * 0.01
        const fx = dx / dist * force
        const fy = dy / dist * force
        a.vx += fx; a.vy += fy
        b.vx -= fx; b.vy -= fy
      }

      // Center gravity
      for (const n of nodes) {
        n.vx += (centerX - n.x) * 0.001
        n.vy += (centerY - n.y) * 0.001
      }

      // Apply velocities
      for (const n of nodes) {
        n.vx *= 0.85
        n.vy *= 0.85
        n.x += n.vx
        n.y += n.vy
        n.x = Math.max(n.radius, Math.min(W - n.radius, n.x))
        n.y = Math.max(n.radius, Math.min(H - n.radius, n.y))
      }

      draw()
      animRef.current = requestAnimationFrame(tick)
    }

    function draw() {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, W, H)

      // Edges
      for (const edge of edgesRef.current) {
        const a = nodesRef.current.find((n) => n.id === edge.source)
        const b = nodesRef.current.find((n) => n.id === edge.target)
        if (!a || !b) continue
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = '#cbd5e1'
        ctx.lineWidth = 1
        if (hovered === a.id || hovered === b.id || selected === a.id || selected === b.id) {
          ctx.strokeStyle = '#2563eb'
          ctx.lineWidth = 2
        }
        ctx.stroke()
      }

      // Nodes
      for (const n of nodesRef.current) {
        const r = n.isSpof ? n.radius + 5 : n.radius
        ctx.beginPath()
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2)

        const isHighlighted = hovered === n.id || selected === n.id
        const isDimmed = selected && selected !== n.id && !edgesRef.current.some(
          (e) => (e.source === selected && e.target === n.id) || (e.target === selected && e.source === n.id)
        )

        ctx.fillStyle = n.isSpof ? COLORS.Critical : COLORS[n.criticality] || '#64748b'
        ctx.globalAlpha = isDimmed ? 0.2 : 1
        ctx.fill()
        ctx.globalAlpha = 1

        if (n.isSpof) {
          ctx.strokeStyle = '#7c3aed'
          ctx.lineWidth = isHighlighted ? 3 : 2
          ctx.stroke()
        } else if (isHighlighted) {
          ctx.strokeStyle = '#2563eb'
          ctx.lineWidth = 3
          ctx.stroke()
        }

        // Label
        ctx.fillStyle = '#1e293b'
        ctx.font = Math.min(11, r * 0.5) + 'px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(n.label, n.x, n.y + r + 12)
      }
    }

    tick()

    return () => {
      running = false
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [employees, dependencies, width, height])

  const handleMouseMove = useCallback((e) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const node = nodesRef.current.find((n) => {
      const dx = mx - n.x, dy = my - n.y
      return Math.sqrt(dx * dx + dy * dy) < (n.isSpof ? n.radius + 10 : n.radius + 5)
    })
    setHovered(node?.id || null)
    canvas.style.cursor = node ? 'pointer' : 'default'
  }, [])

  const handleClick = useCallback((e) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const node = nodesRef.current.find((n) => {
      const dx = mx - n.x, dy = my - n.y
      return Math.sqrt(dx * dx + dy * dy) < (n.isSpof ? n.radius + 10 : n.radius + 5)
    })
    if (node) {
      setSelected(node.id === selected ? null : node.id)
      onNodeClick?.(node.id)
    }
  }, [selected, onNodeClick])

  return (
    <div className="relative bg-white rounded-lg border border-gray-200 overflow-hidden">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        className="w-full"
      />
      <div className="absolute bottom-3 left-3 flex gap-3 text-xs">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-purple-600 inline-block" /> SPOF</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-red-500 inline-block" /> High Criticality</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-amber-500 inline-block" /> Medium</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500 inline-block" /> Low</span>
      </div>
      {hovered && (
        <div className="absolute top-3 right-3 bg-gray-900 text-white px-3 py-1.5 rounded-lg text-xs">
          {hovered}
        </div>
      )}
    </div>
  )
}
