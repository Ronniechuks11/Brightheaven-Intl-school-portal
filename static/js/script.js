const menuToggle = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
});

const reveals = document.querySelectorAll(".reveal");

function revealSections() {

    reveals.forEach(section => {

        const top = section.getBoundingClientRect().top;

        const windowHeight = window.innerHeight;

        if (top < windowHeight - 120) {

            section.classList.add("active");

        }

    });

}

window.addEventListener("scroll", revealSections);

window.addEventListener("load", revealSections);

const counters = document.querySelectorAll(".counter");

const observer = new IntersectionObserver((entries) => {

    entries.forEach(entry => {

        if(entry.isIntersecting){

            const counter = entry.target;

            const target = +counter.dataset.target;

            let count = 0;

            const speed = target / 80;

            function update(){

                count += speed;

                if(count < target){

                    if(counter.classList.contains("percent")){
                        counter.innerHTML = Math.floor(count) + "%";
                    }else{
                        counter.innerHTML = Math.floor(count) + "+";
                    }

                    requestAnimationFrame(update);

                }else{

                    if(counter.classList.contains("percent")){
                        counter.innerHTML = target + "%";
                    }else{
                        counter.innerHTML = target + "+";
                    }

                }

            }

            update();

            observer.unobserve(counter);

        }

    });

},{
    threshold:0.5
});

counters.forEach(counter=>{
    observer.observe(counter);
});

window.addEventListener("load", () => {

    const loader = document.getElementById("loader");

    setTimeout(() => {

        loader.style.opacity = "0";
        loader.style.transition = ".7s ease";

        setTimeout(() => {

            loader.style.display = "none";

        },700);

    },1800);

});