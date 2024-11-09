// Create the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('earth-container').appendChild(renderer.domElement);

// Create the Earth geometry and material
const geometry = new THREE.SphereGeometry(1, 32, 32);
const texture = new THREE.TextureLoader().load('https://threejsfundamentals.org/threejs/resources/images/earth.jpg');
const material = new THREE.MeshBasicMaterial({ map: texture });
const earth = new THREE.Mesh(geometry, material);
scene.add(earth);

// Position the camera
camera.position.z = 3;

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Handle scroll event to rotate the Earth
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    earth.rotation.y = scrollY * 0.01;
});