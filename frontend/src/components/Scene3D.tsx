import { useEffect, useRef } from 'react'
import './Scene3D.css'

const Scene3D = () => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Cargar Three.js
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'

    const initScene = () => {

      const THREE = (window as any).THREE
      if (!THREE) return

      const container = containerRef.current
      if (!container) return

      // Dimensiones
      const width = container.clientWidth
      const height = container.clientHeight

      // Escena, cámara, renderer
      const scene = new THREE.Scene()
      scene.background = new THREE.Color(0x4A90E2)

      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      camera.position.z = 50

      const renderer = new THREE.WebGLRenderer()
      renderer.setSize(width, height)
      renderer.setPixelRatio(window.devicePixelRatio)
      container.appendChild(renderer.domElement)

      // Luz
      const light = new THREE.DirectionalLight(0xffffff, 1)
      light.position.set(5, 5, 5)
      scene.add(light)

      // Pasto (plano)
      const grassGeometry = new THREE.PlaneGeometry(200, 200)
      const grassMaterial = new THREE.MeshStandardMaterial({ color: 0x4CAF50 })
      const grass = new THREE.Mesh(grassGeometry, grassMaterial)
      grass.rotation.x = -Math.PI / 2
      scene.add(grass)

      // Carretera en U - segmento izquierdo
      const roadGeo1 = new THREE.PlaneGeometry(10, 100)
      const roadMat = new THREE.MeshStandardMaterial({ color: 0x333333 })
      const road1 = new THREE.Mesh(roadGeo1, roadMat)
      road1.rotation.x = -Math.PI / 2
      road1.position.set(-15, 0.01, 0)
      scene.add(road1)

      // Carretera - segmento derecho
      const road2 = new THREE.Mesh(roadGeo1, roadMat)
      road2.rotation.x = -Math.PI / 2
      road2.position.set(15, 0.01, 0)
      scene.add(road2)

      // Auto 1
      const carGeo = new THREE.BoxGeometry(4, 2, 8)
      const carMat = new THREE.MeshStandardMaterial({ color: 0x667EEA })
      const car1 = new THREE.Mesh(carGeo, carMat)
      car1.position.set(-15, 1, -20)
      car1.userData.speed = 0.5
      scene.add(car1)

      // Auto 2
      const carMat2 = new THREE.MeshStandardMaterial({ color: 0x9C27B0 })
      const car2 = new THREE.Mesh(carGeo, carMat2)
      car2.position.set(15, 1, -20)
      car2.userData.speed = 0.5
      scene.add(car2)

      // Animación
      const animate = () => {
        requestAnimationFrame(animate)
        renderer.render(scene, camera)
      }
      animate()

      // Resize
      const handleResize = () => {
        const w = container.clientWidth
        const h = container.clientHeight
        camera.aspect = w / h
        camera.updateProjectionMatrix()
        renderer.setSize(w, h)
      }
      window.addEventListener('resize', handleResize)

      return () => window.removeEventListener('resize', handleResize)
    }

    script.onload = initScene
    document.head.appendChild(script)

    return () => {
      const scriptElm = document.querySelector('script[src*="three.min.js"]')
      if (scriptElm) scriptElm.remove()
    }

  }, [])

  return <div ref={containerRef} className="scene-3d"></div>
}

export default Scene3D
