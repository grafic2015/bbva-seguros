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

      // Auto 1 (azul)
      const carGeo = new THREE.BoxGeometry(4, 2, 8)
      const carMat = new THREE.MeshStandardMaterial({ color: 0x667EEA })
      const car1 = new THREE.Mesh(carGeo, carMat)
      car1.position.set(-15, 1, -20)
      car1.userData = {
        speed: 0,
        x: -15,
        z: -20,
        vx: 0,
        vz: 0,
      }
      scene.add(car1)

      // Auto 2 (morado)
      const carMat2 = new THREE.MeshStandardMaterial({ color: 0x9C27B0 })
      const car2 = new THREE.Mesh(carGeo, carMat2)
      car2.position.set(15, 1, -20)
      car2.userData = {
        speed: 0,
        x: 15,
        z: -20,
        vx: 0,
        vz: 0,
      }
      scene.add(car2)

      // Controles
      const keys = {
        ArrowUp: false,
        ArrowDown: false,
        ArrowLeft: false,
        ArrowRight: false,
        w: false,
        a: false,
        s: false,
        d: false,
      }

      window.addEventListener('keydown', (e) => {
        const key = e.key.toLowerCase()
        if (key in keys) keys[key as keyof typeof keys] = true
      })

      window.addEventListener('keyup', (e) => {
        const key = e.key.toLowerCase()
        if (key in keys) keys[key as keyof typeof keys] = false
      })

      // Límites de la carretera
      const roadLeftX = -15
      const roadRightX = 15
      const roadWidth = 5
      const roadMinZ = -50
      const roadMaxZ = 50

      // Animación
      const animate = () => {
        requestAnimationFrame(animate)

        // Actualizar car1 (flechas)
        if (keys.ArrowUp) car1.userData.vz = -0.5
        else if (keys.ArrowDown) car1.userData.vz = 0.5
        else car1.userData.vz *= 0.9

        if (keys.ArrowLeft) car1.userData.vx = -0.3
        else if (keys.ArrowRight) car1.userData.vx = 0.3
        else car1.userData.vx *= 0.9

        // Actualizar car2 (WASD)
        if (keys.w) car2.userData.vz = -0.5
        else if (keys.s) car2.userData.vz = 0.5
        else car2.userData.vz *= 0.9

        if (keys.a) car2.userData.vx = -0.3
        else if (keys.d) car2.userData.vx = 0.3
        else car2.userData.vx *= 0.9

        // Auto-piloto si no hay input
        const car1HasInput = keys.ArrowUp || keys.ArrowDown || keys.ArrowLeft || keys.ArrowRight
        const car2HasInput = keys.w || keys.a || keys.s || keys.d

        if (!car1HasInput) {
          car1.userData.vz = Math.max(car1.userData.vz - 0.02, -0.3)
          // Mantener en carretera
          if (car1.userData.vx > 0.5) car1.userData.vx -= 0.1
          else if (car1.userData.vx < -0.5) car1.userData.vx += 0.1
          else car1.userData.vx *= 0.95
        }

        if (!car2HasInput) {
          car2.userData.vz = Math.max(car2.userData.vz - 0.02, -0.3)
          // Mantener en carretera
          if (car2.userData.vx > 0.5) car2.userData.vx -= 0.1
          else if (car2.userData.vx < -0.5) car2.userData.vx += 0.1
          else car2.userData.vx *= 0.95
        }

        // Actualizar posiciones
        car1.userData.x += car1.userData.vx
        car1.userData.z += car1.userData.vz
        car2.userData.x += car2.userData.vx
        car2.userData.z += car2.userData.vz

        // Límites horizontales (mantener en carretera)
        car1.userData.x = Math.max(roadLeftX - roadWidth, Math.min(roadLeftX + roadWidth, car1.userData.x))
        car2.userData.x = Math.max(roadRightX - roadWidth, Math.min(roadRightX + roadWidth, car2.userData.x))

        // Límites verticales (carretera)
        car1.userData.z = Math.max(roadMinZ, Math.min(roadMaxZ, car1.userData.z))
        car2.userData.z = Math.max(roadMinZ, Math.min(roadMaxZ, car2.userData.z))

        // Aplicar posiciones
        car1.position.x = car1.userData.x
        car1.position.z = car1.userData.z
        car2.position.x = car2.userData.x
        car2.position.z = car2.userData.z

        // Rotación basada en velocidad
        if (Math.abs(car1.userData.vx) > 0.05) {
          car1.rotation.y = Math.atan2(car1.userData.vx, car1.userData.vz)
        }
        if (Math.abs(car2.userData.vx) > 0.05) {
          car2.rotation.y = Math.atan2(car2.userData.vx, car2.userData.vz)
        }

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

      return () => {
        window.removeEventListener('resize', handleResize)
      }
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
