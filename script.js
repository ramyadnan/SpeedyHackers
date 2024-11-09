// Create the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('earth-container').appendChild(renderer.domElement);

// Add lighting
const ambientLight = new THREE.AmbientLight(0x404040); // Soft white light
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5).normalize();
scene.add(directionalLight);

// Create the Earth geometry and material
const geometry = new THREE.SphereGeometry(1, 32, 32);
const textureLoader = new THREE.TextureLoader();
let earth;

textureLoader.load(
    'https://static.wikia.nocookie.net/planet-texture-maps/images/a/aa/Earth_Texture_Full.png/revision/latest?cb=20190401163425', // New texture URL
    (texture) => {
        console.log('Texture loaded', texture);
        const material = new THREE.MeshStandardMaterial({ map: texture });
        earth = new THREE.Mesh(geometry, material);
        scene.add(earth);

        // Handle scroll event to rotate the Earth
        window.addEventListener('scroll', () => {
            if (earth) {
                const scrollY = window.scrollY;
                earth.rotation.y = scrollY * 0.01;
            }
        });
    },
    undefined,
    (err) => {
        console.error('An error happened', err);
    }
);

// Position the camera
camera.position.z = 3;

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();