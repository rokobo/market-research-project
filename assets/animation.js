// Confetti animation, inspired bv https://codepen.io/uiswarup/pen/YzJEPNe
const gravity = 0.5;const terminalVelocity = 5;const drag = 0.075;const confettiQuantityRatio = 5000;
const colors = [
    { front: '#FF0000', back: '#8B0000' },
    { front: '#00cc00', back: '#006400' },
    { front: '#0000FF', back: '#00008B' },
    { front: '#FFFF00', back: '#b3b300' },
    { front: '#FFA500', back: '#805300' },
    { front: '#FFC0CB', back: '#800015' },
    { front: '#990099', back: '#660066' },
    { front: '#40E0D0', back: '#126e64' }];
randomRange = (min, max) => Math.random() * (max - min) + min;

function animateConfetti() {
    let confetti = [];
    var retryInterval = setInterval(function() {
        console.log("Began confetti animation");
        const canvas = document.getElementById("confetti");
        if (canvas) {
            clearInterval(retryInterval);
            const ctx = canvas.getContext("2d");
            function setCanvasSize() {
                canvas.width = window.innerWidth;
                canvas.height = Math.max(document.body.scrollHeight, window.innerHeight);
                confettiCount = (canvas.width * canvas.height / confettiQuantityRatio) | 0;
                console.log("Canvas set to " + canvas.width + "x" + canvas.height);
                console.log("Using " + confettiCount + " units of confetti");
            }
            setCanvasSize();
            class Confetti {
                constructor() {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.color = colors[Math.floor(Math.random() * colors.length)];
                    this.size_x = (Math.random() * 10) + 10;
                    this.size_y = (Math.random() * 20) + 10;
                    this.rotation = Math.random() * 2 * Math.PI;
                    this.rotation_speed_y = ((Math.random() * 5) / 100) + 0.05;
                    this.rotation_speed_z = Math.random() / 10;
                    this.scale_x = 1;
                    this.scale_y = 1;
                    this.velocity_x = (Math.random() * 50) - 25;
                    this.velocity_y = Math.random() * -50;
                    this.width = this.size_x * this.scale_x;
                    this.height =  this.size_y * this.scale_y;
                }
                update() {
                    // Move canvas to position and rotate
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation);

                    // Apply forces to velocity
                    this.velocity_x -= this.velocity_x * drag;
                    this.velocity_y = Math.min(this.velocity_y + gravity, terminalVelocity);
                    this.velocity_x += Math.random() > 0.5 ? Math.random() : -Math.random();

                    // Set position
                    this.x += this.velocity_x;
                    this.y += this.velocity_y;

                    // Apply rotation along the z axis
                    this.rotation = this.rotation + this.rotation_speed_z;
                    if (this.rotation > Math.PI * 2) {this.rotation = 0;}
                }
                draw() {
                    this.width = this.size_x * this.scale_x;
                    this.height =  this.size_y * this.scale_y;

                    // Loop confetto x position
                    if (this.x > canvas.width) {this.x = 0}
                    if (this.x < 0) {this.x = canvas.width}

                    // Spin confetto by scaling y, draw, reset transform matrix
                    this.scale_y = Math.cos(this.y * this.rotation_speed_y);
                    ctx.fillStyle = this.scale_y > 0 ? this.color.front : this.color.back;
                    ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
                    ctx.setTransform(1, 0, 0, 1, 0, 0);
                }
            }
            function createConfetti() {for (let i = 0; i < confettiCount; i++) {confetti.push(new Confetti());}}
            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                confetti.forEach((confetto, index) => {
                    confetto.update();
                    // Delete confetti when out of frame, else draw
                    if (confetto.y >= canvas.height) {confetti.splice(index, 1);}
                    else {confetto.draw();}
                });
                if (confetti.length > 0) {requestAnimationFrame(animate);}
                else {console.log("Finished confetti animation")}
            }
            createConfetti();animate();
        }
    }, 500)
};

var retryInterval = setInterval(function() {
    const save_button = document.getElementById("save-products");
    if (save_button) {
        console.log("First button element found");
        clearInterval(retryInterval);
        save_button.addEventListener("click", function() {
            console.log("First button clicked");
            var retryInterval2 = setInterval(function() {
                const save_button = document.getElementById("close-send-confirmation");
                if (save_button) {
                    console.log("Second button element found");
                    clearInterval(retryInterval2);
                    save_button.addEventListener("click", function() {
                        console.log("Second button clicked");
                        animateConfetti();
                    }, 1000)
                }
            });
        }, 1000)
    }
});
