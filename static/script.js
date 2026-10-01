// FITNESS ANALYTICS CHART

const ctx =
document.getElementById(
    'fitnessChart'
);

if(ctx){

    const chartLabels =
    JSON.parse(
        document
        .getElementById(
            'fitnessChart'
        )
        .dataset
        .labels || '[]'
    );

    const chartValues =
    JSON.parse(
        document
        .getElementById(
            'fitnessChart'
        )
        .dataset
        .values || '[]'
    );

    new Chart(ctx, {

        type: 'line',

        data: {

            labels: chartLabels,

            datasets: [{

                label: 'Calories Burned',

                data: chartValues,

                borderColor: '#8b5cf6',

                backgroundColor:
                'rgba(139,92,246,0.2)',

                fill: true,

                tension: 0.4,

                borderWidth: 3,

                pointRadius: 5,

                pointHoverRadius: 8
            }]
        },

        options: {

            responsive: true,

            plugins: {

                legend: {

                    labels: {

                        color: 'white',

                        font: {

                            size: 14
                        }
                    }
                }
            },

            scales: {

                x: {

                    ticks: {

                        color: 'white'
                    },

                    grid: {

                        color:
                        'rgba(255,255,255,0.05)'
                    }
                },

                y: {

                    ticks: {

                        color: 'white'
                    },

                    grid: {

                        color:
                        'rgba(255,255,255,0.05)'
                    }
                }
            }
        }
    });
}

// METRIC CARD ANIMATION

const cards =
document.querySelectorAll(
    '.metric-card'
);

cards.forEach((card,index)=>{

    card.style.opacity = '0';

    card.style.transform =
    'translateY(40px)';

    setTimeout(()=>{

        card.style.transition =
        '0.6s ease';

        card.style.opacity = '1';

        card.style.transform =
        'translateY(0px)';

    },index * 200);
});

// HISTORY TABLE ANIMATION

const rows =
document.querySelectorAll(
    'table tr'
);

rows.forEach((row,index)=>{

    row.style.opacity = '0';

    setTimeout(()=>{

        row.style.transition =
        '0.5s ease';

        row.style.opacity = '1';

    },index * 100);
});

// BUTTON HOVER EFFECT

const addBtn =
document.querySelector(
    '.add-btn'
);

if(addBtn){

    addBtn.addEventListener(
        'mouseenter',
        ()=>{

            addBtn.style.transform =
            'scale(1.05)';
        }
    );

    addBtn.addEventListener(
        'mouseleave',
        ()=>{

            addBtn.style.transform =
            'scale(1)';
        }
    );
}

// SCROLL REVEAL EFFECT

const revealElements =
document.querySelectorAll(
    '.chart-card,.recommendation-card,.history-card'
);

window.addEventListener(
    'scroll',
    ()=>{

        revealElements.forEach(element=>{

            const position =
            element
            .getBoundingClientRect()
            .top;

            const screenHeight =
            window.innerHeight;

            if(position < screenHeight - 100){

                element.style.opacity = '1';

                element.style.transform =
                'translateY(0px)';
            }
        });
    }
);

// INITIAL HIDDEN STATE

revealElements.forEach(element=>{

    element.style.opacity = '0';

    element.style.transform =
    'translateY(50px)';

    element.style.transition =
    '0.8s ease';
});

// LIVE CLOCK

const userInfo =
document.querySelector(
    '.user-info'
);

if(userInfo){

    const clock =
    document.createElement('div');

    clock.style.fontSize = '14px';

    clock.style.marginTop = '8px';

    clock.style.color = '#d1d5db';

    userInfo.appendChild(clock);

    function updateClock(){

        const now =
        new Date();

        clock.innerHTML =
        now.toLocaleString();
    }

    setInterval(updateClock,1000);

    updateClock();
}