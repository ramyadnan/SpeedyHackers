// Create the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true }); // Enable alpha for transparent background
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('earth-container').appendChild(renderer.domElement);

// Remove the black background
renderer.setClearColor(0x000000, 0); // Set background to transparent

// Add lighting
const ambientLight = new THREE.AmbientLight(0x404040); // Soft white light
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5).normalize();
scene.add(directionalLight);

// Create the hourglass geometry and material
const topConeGeometry = new THREE.ConeGeometry(1, 2, 32);
const bottomConeGeometry = new THREE.ConeGeometry(1, 2, 32);
const material = new THREE.MeshStandardMaterial({ color: 0x8B4513 });

const topCone = new THREE.Mesh(topConeGeometry, material);
const bottomCone = new THREE.Mesh(bottomConeGeometry, material);

// Adjust the positions of the cones
topCone.position.y = 1;
bottomCone.position.y = -1;

// Adjust the rotations of the cones
topCone.rotation.x = Math.PI;
bottomCone.rotation.x = 0;

// Add the cones to the scene
scene.add(topCone);
scene.add(bottomCone);

// Position the camera
camera.position.z = 5;

// Animation loop
function animate() {
    requestAnimationFrame(animate);

    // Use the same rotation value for both cones
    const rotationSpeed = 0.01;
    topCone.rotation.y += rotationSpeed;
    bottomCone.rotation.y += rotationSpeed;

    renderer.render(scene, camera);
}
animate();