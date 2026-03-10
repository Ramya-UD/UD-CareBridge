const impactData = [
{
name: "Sindhutai Sapkal",
type: "Mother of Orphans",
tickerInfo: "Adopted 1000+ orphan children",
learnInfo: "Raised abandoned children as a single mother and built homes across Maharashtra. Child protection & rehabilitation.       Children are not a burden — they are responsibility.",
place: "India",
image: "https://sindhutaisapkal.org/images/team_maai.jpg"
},
{
name: "Miracle Foundation India",
type: "Child Welfare NGO",
tickerInfo: "Supports orphaned children education",
learnInfo: "Focuses on deinstitutionalization — helping children grow in family-based care. Education, health, emotional development. Every child deserves a family. ",
place: "India",
image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAJlxr6RMd12oR54KqQceJzgaZ0FnYiRpv8Q&s"
},
{
name: "SOS Children's Villages",
type: "Global Organization",
tickerInfo: "Family-based care for orphans",
learnInfo: "Operates in 130+ countries creating stable family environments. Family homes, education, skill building.     No child should grow up alone.",
place: "Worldwide",
image: "https://www.sos-childrensvillages.org/App_Themes/sos/images/country-images/facebook-default.jpg"
},
{
name: "Akshaya Patra Foundation",
type: "Meal Support NGO",
tickerInfo: "Feeds millions of children daily",
learnInfo: "Runs one of the world’s largest NGO-run school meal programs.Mid-day meals program.      No child should study hungry.",
place: "India",
image: "https://indiacsr.in/wp-content/uploads/2020/08/Shridhar-Venkat-CEO-Akshaya-Patra-Foundation-at-India-CSR-Network.jpg"
}
];




const track = document.getElementById("tickerTrack");
const learnGrid = document.getElementById("learnGrid");

/* MOVING CARDS */
function createTicker(list){
list.forEach(d=>{
const card = document.createElement("div");
card.className = "ticker-card";

card.innerHTML = `
<img src="${d.image}" loading="lazy"
onerror="this.src='https://via.placeholder.com/80?text=NGO'">
<div>
<strong>${d.name}</strong><br>
${d.tickerInfo}<br>
📍 ${d.place}
</div>
`;
track.appendChild(card);
});
}

/* LEARNING CARDS WITH EXTRA INFO */
function createLearningCards(list){
list.forEach(d=>{
const box = document.createElement("div");
box.className = "learn-card";

box.innerHTML = `
<img src="${d.image}" loading="lazy"
onerror="this.src='https://via.placeholder.com/120?text=NGO'">
<h3>${d.name}</h3>
<p>${d.learnInfo}</p>
<span>${d.type}</span>
`;
learnGrid.appendChild(box);
});
}



createTicker(impactData);
createTicker(impactData);
createLearningCards(impactData);