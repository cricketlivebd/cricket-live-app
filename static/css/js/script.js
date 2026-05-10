const page = window.location.pathname;
const slider = document.querySelector(".slider");

let speed = 1;

function move() {
    if (slider) {
        slider.scrollLeft += speed;

        // 🔥 FIXED RESET
        if (slider.scrollLeft >= slider.scrollWidth / 2) {
            slider.scrollLeft = 0;
        }
    }
}

setInterval(move, 20);

const hostInput = document.getElementById("hostTeam");
const visitorInput = document.getElementById("visitorTeam");

const hostLabel = document.getElementById("hostLabel");
const visitorLabel = document.getElementById("visitorLabel");

// 🔥 live update
if (hostInput && hostLabel) {
    hostInput.addEventListener("input", function () {
        hostLabel.textContent = hostInput.value || "Host Team";
    });
}

if (visitorInput && visitorLabel) {
    visitorInput.addEventListener("input", function () {
        visitorLabel.textContent = visitorInput.value || "Visitor Team";
    });
}

function goToOpening() {
    window.location.href = "/opening-players";
}

function startMatch() {
    window.location.href = "/live-match";
}

function validateMatch() {

    const host = document.getElementById("hostTeam");
    const visitor = document.getElementById("visitorTeam");
    const overs = document.getElementById("overs");

    const toss = document.querySelector('input[name="toss"]:checked');
    const opt = document.querySelector('input[name="opt"]:checked');

    if (!host.value.trim()) {
        host.focus();
        alert("Enter Host Team");
        return;
    }

    if (!visitor.value.trim()) {
        visitor.focus();
        alert("Enter Visitor Team");
        return;
    }

    if (!toss) {
        alert("Select Toss Winner");
        return;
    }

    if (!opt) {
        alert("Select Bat or Bowl");
        return;
    }

    if (!overs.value) {
        overs.focus();
        alert("Enter Overs");
        return;
    }

    const tossValue = toss.value;
    const optValue = opt.value;

    const url = `/save-match?host=${encodeURIComponent(host.value)}&visitor=${encodeURIComponent(visitor.value)}&toss=${tossValue}&opt=${optValue}&overs=${overs.value}`;

    window.location.href = url;
}

function validateOpening() {

    const striker = document.getElementById("striker");
    const nonStriker = document.getElementById("nonStriker");
    const bowler = document.getElementById("bowler");

    if (!striker.value.trim()) {
        striker.focus();
        alert("Enter Striker Name");
        return;
    }

    if (!nonStriker.value.trim()) {
        nonStriker.focus();
        alert("Enter Non-Striker Name");
        return;
    }

    if (!bowler.value.trim()) {
        bowler.focus();
        alert("Enter Bowler Name");
        return;
    }

    // 🔥 backend e pathabo
    const url = `/save-opening?striker=${encodeURIComponent(striker.value)}&nonStriker=${encodeURIComponent(nonStriker.value)}&bowler=${encodeURIComponent(bowler.value)}`;

    window.location.href = url;
}

function saveSettings() {

    const players = document.querySelector('[name="players"]').value;

    const noball = document.querySelector('[name="noball"]').checked ? 1 : 0;
    const noball_reball = document.querySelector('[name="noball_reball"]').checked ? 1 : 0;
    const noball_run = document.querySelector('[name="noball_run"]').value;

    const wide = document.querySelector('[name="wide"]').checked ? 1 : 0;
    const wide_reball = document.querySelector('[name="wide_reball"]').checked ? 1 : 0;
    const wide_run = document.querySelector('[name="wide_run"]').value;

    // 🔥 backend e pathabo
    const url = `/save-settings?players=${players}&noball=${noball}&noball_reball=${noball_reball}&noball_run=${noball_run}&wide=${wide}&wide_reball=${wide_reball}&wide_run=${wide_run}`;

    window.location.href = url;
}

let extraTotal = 0;
let extraLB = 0;
let extraB = 0;
let extraWD = 0;
let extraNB = 0;
let partnerships = [];
// 🔥 current running partnership
let pRuns = 0;
let pBalls = 0;
if (page.includes("live-match") || page.includes("match")) {

    let score = 0;
    let ball = 0;
    let over = 0;
    let wickets = 0;
    let strikerRuns = 0;
    let strikerBalls = 0;
    let striker4 = 0;
    let striker6 = 0;
    let striker = "";
    let nonStriker = "";
    let nonStrikerRuns = 0;
    let nonStrikerBalls = 0;
    let nonStriker4 = 0;
    let nonStriker6 = 0;
    let bowlerRuns = 0;
    let bowlerBalls = 0;
    let bowlerWickets = 0;
    let bowlerMaiden = 0;
    let overRuns = 0;
    let thisOver = [];
    
    

    window.onload = function(){

        // 🔥 SCORE
        const scoreText = document.getElementById("score").innerText;
        const overText = document.getElementById("over").innerText;

        score = parseInt(scoreText.split(" - ")[0]) || 0;
        wickets = parseInt(scoreText.split(" - ")[1]) || 0;

        let overParts = overText.split(".");
        over = parseInt(overParts[0]) || 0;
        ball = parseInt(overParts[1]) || 0;

        // 🔥 PLAYER NAME
        const s = document.getElementById("strikerName");
        const ns = document.getElementById("nonStrikerName");

        if(s && ns){
            striker = s.innerText.replace(" *", "");
            nonStriker = ns.innerText;
        }

        // 🔥 STRIKER
        strikerRuns = parseInt(document.getElementById("sRuns").innerText) || 0;
        strikerBalls = parseInt(document.getElementById("sBalls").innerText) || 0;
        striker4 = parseInt(document.getElementById("s4").innerText) || 0;
        striker6 = parseInt(document.getElementById("s6").innerText) || 0;

        // 🔥 NON STRIKER
        nonStrikerRuns = parseInt(document.getElementById("nsRuns").innerText) || 0;
        nonStrikerBalls = parseInt(document.getElementById("nsBalls").innerText) || 0;
        nonStriker4 = parseInt(document.getElementById("ns4").innerText) || 0;
        nonStriker6 = parseInt(document.getElementById("ns6").innerText) || 0;

        // 🔥 BOWLER
        bowlerRuns = parseInt(document.getElementById("bRun").innerText) || 0;
        bowlerWickets = parseInt(document.getElementById("bWicket").innerText) || 0;
        bowlerMaiden = parseInt(document.getElementById("bMaiden").innerText) || 0;

        let bOverText = document.getElementById("bOver").innerText.split(".");
        bowlerBalls = (parseInt(bOverText[0]) * 6) + parseInt(bOverText[1]);

        // 🔥 THIS OVER
        const overDiv = document.getElementById("thisOver");

        if (overDiv) {
            let overData = overDiv.innerText.trim();
            thisOver = overData ? overData.split(",") : [];
        } else {
            thisOver = [];
        }

        // 🔥 EXTRA
        let extraText = document.getElementById("extraData")?.innerText.trim() || "";

        if(extraText){
            let parts = extraText.split(",");

            extraTotal = parseInt(parts[0]) || 0;
            extraLB = parseInt(parts[1]) || 0;
            extraB = parseInt(parts[2]) || 0;
            extraWD = parseInt(parts[3]) || 0;
            extraNB = parseInt(parts[4]) || 0;
        }
        partnerships = [];
        // 🔥 PARTNERSHIP LOAD (FINAL FIX)
        let pData = document.getElementById("partnerData")?.textContent.trim();

        if(pData && pData !== "[]"){
            try{
                partnerships = JSON.parse(pData);
            }catch(e){
                console.log("PARTNERSHIP ERROR:", pData);
                partnerships = [];
            }
        }

        // 🔥 ONLY IF COMPLETELY EMPTY (FIRST MATCH START)
        if(partnerships.length === 0){
            partnerships.push({
                striker: striker,
                nonStriker: nonStriker,
                runs: 0,
                balls: 0
            });
        }

        // 🔥 START NEW PARTNERSHIP AFTER WICKET
        let last = partnerships[partnerships.length - 1];

        // 🔥 ONLY যদি batsman change হয় (wicket case)
        if(last){

            let samePair =
                (last.striker === striker && last.nonStriker === nonStriker) ||
                (last.striker === nonStriker && last.nonStriker === striker);

            if(!samePair){
                partnerships.push({
                    striker: striker,
                    nonStriker: nonStriker,
                    runs: 0,
                    balls: 0
                });
            }
        }

        // 🔥 SAVE FOR FOW PAGE
        if(striker){
            localStorage.setItem("strikerName", striker);
        }
        if(nonStriker){
            localStorage.setItem("nonStrikerName", nonStriker);
        }

        updateCRR();
        updateRRR();
    };
    function isMaidenOver(overArr) {

        for (let b of overArr) {

            let text = String(b);

            // normal run > 0
            if (!isNaN(text) && Number(text) > 0) {
                return false;
            }

            // wide / no ball
            if (text.includes("WD") || text.includes("NB")) {
                return false;
            }
        }

        return true;
    }
    
    window.addRun = function (run) {

        const wide = document.getElementById("wide").checked;
        const noball = document.getElementById("noball").checked;
        const byes = document.getElementById("byes").checked;
        const legbyes = document.getElementById("legbyes").checked;
        const wicket = document.getElementById("wicket").checked;

        // 🔴 WICKET
        if (wicket) {

            let outPlayer = striker;

            strikerRuns += run;
            strikerBalls++;

            let sr = strikerBalls === 0 ? 0 : ((strikerRuns / strikerBalls) * 100).toFixed(2);

            let outData = `${outPlayer}=${strikerRuns},${strikerBalls},${striker4},${striker6},${sr}`;

            score += run;
            
            if (ball < 6) {
                ball++;
            }
            wickets++;
            bowlerBalls++;

            overRuns += run;
            thisOver.push("W");

            // 🔥 RESET PARTNERSHIP
            pRuns = 0;
            pBalls = 0;
            // 🔥 START NEW PARTNERSHIP (NEW BATSMAN আসার পর)
            setTimeout(() => {
                partnerships.push({
                    striker: "",   // temporary
                    nonStriker: nonStriker,
                    runs: 0,
                    balls: 0
                });
            }, 300);
            let innings = document.getElementById("inningsData")?.innerText.trim();

            let totalOvers = parseInt(document.getElementById("oversData")?.innerText.trim()) || 0;
            let players = parseInt(document.getElementById("playersData")?.innerText.trim()) || 11;
            let maxWickets = players - 1;

            let totalBallsPlayed = over * 6 + ball;
            let totalBallsMatch = totalOvers * 6;
            let overEnded = false;
            let finishedOver = thisOver.join(",");

            if (ball >= 6) {

                if (isMaidenOver(thisOver)) {
                    bowlerMaiden++;
                }

                overRuns = 0;
                thisOver = [];
            
                over++;
                ball = 0;

                overEnded = true;
            }
            let pSend = partnerships.length > 0 ? JSON.stringify(partnerships) : null;
            fetch("/update-score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    score, wickets, over, ball,

                    striker, non_striker: nonStriker,

                    s_runs: strikerRuns,
                    s_balls: strikerBalls,
                    s_4: striker4,
                    s_6: striker6,

                    ns_runs: nonStrikerRuns,
                    ns_balls: nonStrikerBalls,
                    ns_4: nonStriker4,
                    ns_6: nonStriker6,

                    b_runs: bowlerRuns,
                    b_balls: bowlerBalls,
                    b_wickets: bowlerWickets,
                    b_maiden: bowlerMaiden,

                    this_over: thisOver.join(","),
                    finished_over: overEnded ? finishedOver : "",

                    s_sr: strikerBalls === 0 ? 0 : ((strikerRuns / strikerBalls) * 100).toFixed(2),
                    ns_sr: nonStrikerBalls === 0 ? 0 : ((nonStrikerRuns / nonStrikerBalls) * 100).toFixed(2),
                    b_er: (bowlerBalls === 0) ? 0 : (bowlerRuns / (bowlerBalls / 6)).toFixed(2),

                    out_player: outPlayer,
                    out_stats: outData,
                    over_ended: overEnded,
                    wicket_type: localStorage.getItem("wicketType") || "pending",
                    extra: `${extraTotal},${extraLB}LB,${extraB}B,${extraWD}WD,${extraNB}NB`,
                    partnerships: pSend
                })
            }).then(() => {
                 // 🔥 SECOND INNINGS RESULT CHECK FIRST
                    if(innings == "2"){
                        let ended = checkMatchResultDirect(score, wickets, over, ball);
                        if(ended) return; // 🔥 STOP redirect
                    }

                    // 🔥 FIRST INNINGS END
                    if (innings == "1" && (wickets >= maxWickets || totalBallsPlayed == totalBallsMatch)) {

                        let target = score + 1;
                        openInningsModal(target, totalOvers);

                    } else {

                localStorage.setItem("overEnded", overEnded);
                window.location.href = `/fall-of-wicket`;
                }
            });

            return;
        }

        // 🔵 WIDE
        if (wide) {

            // 🔥 EXTRA UPDATE
            extraTotal += 1 + run;
            extraWD += 1;

            if(run > 0){
                extraB += run;
            }

            score += 1 + run;
            bowlerRuns += 1 + run;
            overRuns += 1 + run;

            // 🔥 PARTNERSHIP UPDATE
            pRuns += (1 + run);

            

            let current = partnerships[partnerships.length - 1];
            current.runs += (1 + run);

            thisOver.push(run > 0 ? run + "WD" : "WD");

            if (run % 2 === 1) swapStrike();

            resetChecks();
            updateUI();
            return;
        }

        // 🔵 NO BALL
        if (noball) {

            // 🔥 EXTRA UPDATE
            extraTotal += 1 + run;
            extraNB += 1;

            if(run > 0){
                extraB += run;
            }

            score += 1 + run;
            bowlerRuns += 1 + run;
            overRuns += 1 + run;

            strikerRuns += run;
            strikerBalls++;

            // 🔥 PARTNERSHIP UPDATE
            pRuns += (1 + run);

            if(partnerships.length === 0){
                partnerships.push({
                    striker: striker,
                    nonStriker: nonStriker,
                    runs: 0,
                    balls: 0
                });
            }

            let current = partnerships[partnerships.length - 1];
            current.runs += (1 + run);

            thisOver.push(run > 0 ? run + "NB" : "NB");

            if (run % 2 === 1) swapStrike();

            resetChecks();
            updateUI();
            return;
        }

        // 🟡 BYES / LEG BYES
        if (byes || legbyes) {

            // 🔥 EXTRA UPDATE
            extraTotal += run;

            if(byes){
                extraB += run;
            }else{
                extraLB += run;
            }

            score += run;
            if (ball < 6) {
                ball++;
            }
            bowlerBalls++;
            strikerBalls++;
            overRuns += run;

            // 🔥 PARTNERSHIP UPDATE
            pRuns += run;
            pBalls++;

            if(partnerships.length === 0){
                partnerships.push({
                    striker: striker,
                    nonStriker: nonStriker,
                    runs: 0,
                    balls: 0
                });
            }

            let current = partnerships[partnerships.length - 1];
            current.runs += run;
            current.balls++;

            thisOver.push(byes ? (run > 0 ? run + "BYE" : "BYE") : (run > 0 ? run + "LB" : "LB"));
            let innings = document.getElementById("inningsData")?.innerText.trim();

            let totalOvers = parseInt(document.getElementById("oversData")?.innerText.trim()) || 0;
            let players = parseInt(document.getElementById("playersData")?.innerText.trim()) || 11;
            let maxWickets = players - 1;

            let totalBallsPlayed = over * 6 + ball;
            //let totalBallsPlayed = (over - 1) * 6 + 6;
            let totalBallsMatch = totalOvers * 6;

            if (run % 2 === 1) swapStrike();

            if (ball >= 6) {

                if (isMaidenOver(thisOver)) {
                    bowlerMaiden++;
                }

                let finishedOver = thisOver.join(",");

                overRuns = 0;
                thisOver = [];

                over++;
                ball = 0;
                swapStrike();
                let pSend = partnerships.length > 0 ? JSON.stringify(partnerships) : null;
                fetch("/update-score", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        score, wickets, over, ball,

                        striker, non_striker: nonStriker,

                        s_runs: strikerRuns,
                        s_balls: strikerBalls,
                        s_4: striker4,
                        s_6: striker6,

                        ns_runs: nonStrikerRuns,
                        ns_balls: nonStrikerBalls,
                        ns_4: nonStriker4,
                        ns_6: nonStriker6,

                        b_runs: bowlerRuns,
                        b_balls: bowlerBalls,
                        b_wickets: bowlerWickets,
                        b_maiden: bowlerMaiden,

                        this_over: "",
                        finished_over: finishedOver,
                        extra: `${extraTotal},${extraLB}LB,${extraB}B,${extraWD}WD,${extraNB}NB`,
                        partnerships: pSend
                    })
                }).then(() => {

                   // 🔥 SECOND INNINGS RESULT CHECK FIRST
                    if(innings == "2"){
                        let ended = checkMatchResultDirect(score, wickets, over, ball);
                        if(ended) return; // 🔥 STOP redirect
                    }

                    // 🔥 FIRST INNINGS END
                    if (innings == "1" && (wickets >= maxWickets || totalBallsPlayed == totalBallsMatch)) {

                        let target = score + 1;
                        openInningsModal(target, totalOvers);

                    } else {

                        window.location.href = "/choose-bowler";
                    }
                });

                return;
            }

            resetChecks();
            updateUI();
            return;
        }

        // 🔴 NORMAL RUN
        score += run;
        if (ball < 6) {
            ball++;
        }
        bowlerBalls++;
        strikerRuns += run;
        strikerBalls++;

        // 🔥 PARTNERSHIP UPDATE
        pRuns += run;
        pBalls++;

        if(partnerships.length === 0){
            partnerships.push({
                striker: striker,
                nonStriker: nonStriker,
                runs: 0,
                balls: 0
            });
        }

        let current = partnerships[partnerships.length - 1];
        current.runs += run;
        current.balls++;

        thisOver.push(run);
        bowlerRuns += run;
        overRuns += run;

        if (run === 4) striker4++;
        if (run === 6) striker6++;

        if (run % 2 === 1) swapStrike();
        
        if (ball >= 6) {
            let innings = document.getElementById("inningsData")?.innerText.trim();

            let totalOvers = parseInt(document.getElementById("oversData")?.innerText.trim()) || 0;
            let players = parseInt(document.getElementById("playersData")?.innerText.trim()) || 11;
            let maxWickets = players - 1;

            let totalBallsPlayed = over * 6 + ball;
            let totalBallsMatch = totalOvers * 6;

            
            if (isMaidenOver(thisOver)) {
                bowlerMaiden++;
            }

            let finishedOver = thisOver.join(",");

            overRuns = 0;
            thisOver = [];
            
            over++;
            ball = 0;
            swapStrike();
            
        
            let pSend = partnerships.length > 0 ? JSON.stringify(partnerships) : null;
            fetch("/update-score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    score, wickets, over, ball,

                    striker, non_striker: nonStriker,

                    s_runs: strikerRuns,
                    s_balls: strikerBalls,
                    s_4: striker4,
                    s_6: striker6,

                    ns_runs: nonStrikerRuns,
                    ns_balls: nonStrikerBalls,
                    ns_4: nonStriker4,
                    ns_6: nonStriker6,

                    b_runs: bowlerRuns,
                    b_balls: bowlerBalls,
                    b_wickets: bowlerWickets,
                    b_maiden: bowlerMaiden,

                    this_over: "",
                    finished_over: finishedOver,
                    extra: `${extraTotal},${extraLB}LB,${extraB}B,${extraWD}WD,${extraNB}NB`,
                    partnerships: pSend
                })
            }).then(() => {

                    // 🔥 SECOND INNINGS RESULT CHECK FIRST
                    if(innings == "2"){
                        let ended = checkMatchResultDirect(score, wickets, over, ball);
                        if(ended) return; // 🔥 STOP redirect
                    }

                    // 🔥 FIRST INNINGS END
                    if (innings == "1" && (wickets >= maxWickets || totalBallsPlayed == totalBallsMatch)) {

                        let target = score + 1;
                        openInningsModal(target, totalOvers);

                    } else {

                        window.location.href = "/choose-bowler";
                    }

                });

            return;
        }

        updateUI();
    };
    function resetChecks() {
        document.getElementById("wide").checked = false;
        document.getElementById("noball").checked = false;
        document.getElementById("byes").checked = false;
        document.getElementById("legbyes").checked = false;
        document.getElementById("wicket").checked = false;
    }
    function swapStrike() {

        // 🔥 name swap
        let temp = striker;
        striker = nonStriker;
        nonStriker = temp;

        // 🔥 stats swap
        let tempRuns = strikerRuns;
        let tempBalls = strikerBalls;
        let temp4 = striker4;
        let temp6 = striker6;

        strikerRuns = nonStrikerRuns;
        strikerBalls = nonStrikerBalls;
        striker4 = nonStriker4;
        striker6 = nonStriker6;

        nonStrikerRuns = tempRuns;
        nonStrikerBalls = tempBalls;
        nonStriker4 = temp4;
        nonStriker6 = temp6;
    }

   function updateUI() {

        // 🔥 score + over
        document.getElementById("score").innerText = score + " - " + wickets;
        document.getElementById("over").innerText = over + "." + ball;

        // 🔥 batsman name
        document.getElementById("strikerName").innerText = striker + " *";
        document.getElementById("nonStrikerName").innerText = nonStriker;

        // 🔥 STRIKER stats
        document.getElementById("sRuns").innerText = strikerRuns;
        document.getElementById("sBalls").innerText = strikerBalls;
        document.getElementById("s4").innerText = striker4;
        document.getElementById("s6").innerText = striker6;

        let sr = strikerBalls === 0 ? 0 : (strikerRuns / strikerBalls) * 100;
        document.getElementById("sSR").innerText = sr.toFixed(2);

        // 🔥 NON-STRIKER stats (🔥 ETAI MISSING CHILO)
        document.getElementById("nsRuns").innerText = nonStrikerRuns;
        document.getElementById("nsBalls").innerText = nonStrikerBalls;
        document.getElementById("ns4").innerText = nonStriker4;
        document.getElementById("ns6").innerText = nonStriker6;

        let nsSR = nonStrikerBalls === 0 ? 0 : (nonStrikerRuns / nonStrikerBalls) * 100;
        document.getElementById("nsSR").innerText = nsSR.toFixed(2);
        // 🔥 bowler over
        let bOver = Math.floor(bowlerBalls / 6);
        let bBall = bowlerBalls % 6;

        document.getElementById("bOver").innerText = bOver + "." + bBall;
        document.getElementById("bMaiden").innerText = bowlerMaiden;
        document.getElementById("bRun").innerText = bowlerRuns;
        document.getElementById("bWicket").innerText = bowlerWickets;
        updateCRR();
        updateRRR();
        updateNeed();
        checkMatchResult();
        // 🔥 economy
        let overs = bowlerBalls / 6;
        let er = overs === 0 ? 0 : (bowlerRuns / overs);

        document.getElementById("bER").innerText = er.toFixed(2);
        
        let overHTML = "";

        thisOver.forEach(item => {

            let text = item.toString();

            let run = text.match(/\d+/)?.[0] || "";
            let extra = text.replace(run, "");

            if(text === "W"){
                overHTML += `<span class="ball red">W</span>`;
            }
            else if(text === "WD" || text === "NB"){
                overHTML += `<span class="ball gray">${text}</span>`;
            }
            else if(text == 4){
                overHTML += `<span class="ball orange">4</span>`;
            }
            else if(text == 6){
                overHTML += `<span class="ball green">6</span>`;
            }
            else{
                // 🔥 MAIN FIX
                overHTML += `
                    <div class="ball-wrap">
                        <span class="ball">${run}</span>
                        ${extra ? `<small class="extra">${extra}</small>` : ""}
                    </div>
                `;
            }

        });

        document.getElementById("thisOver").innerHTML = overHTML;
        let pSend = partnerships.length > 0 ? JSON.stringify(partnerships) : null;
        // 🔥 BACKEND SAVE
       fetch("/update-score", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                score: score,
                wickets: wickets,
                over: over,
                ball: ball,

                striker: striker,
                non_striker: nonStriker,

                s_runs: strikerRuns,
                s_balls: strikerBalls,
                s_4: striker4,
                s_6: striker6,

                ns_runs: nonStrikerRuns,
                ns_balls: nonStrikerBalls,
                ns_4: nonStriker4,
                ns_6: nonStriker6,

                b_runs: bowlerRuns,
                b_balls: bowlerBalls,
                b_wickets: bowlerWickets,
                b_maiden: bowlerMaiden,
                // 🔥 MAIN ADD
                this_over: thisOver.join(","),
                // 🔥 NEW
                s_sr: strikerBalls === 0 ? 0 : ((strikerRuns / strikerBalls) * 100).toFixed(2),
                ns_sr: nonStrikerBalls === 0 ? 0 : ((nonStrikerRuns / nonStrikerBalls) * 100).toFixed(2),
                b_er: (bowlerBalls === 0) ? 0 : (bowlerRuns / (bowlerBalls / 6)).toFixed(2),

                extra: `${extraTotal},${extraLB}LB,${extraB}B,${extraWD}WD,${extraNB}NB`,
                partnerships: pSend
            })
        });
        // 🔥 extra save (batsman + bowler)
        
    }
}
function updateCRR(){

    let scoreText = document.getElementById("score").innerText;
    let overText = document.getElementById("over").innerText;

    // 🔥 score parse
    let score = parseInt(scoreText.split(" - ")[0]) || 0;

    // 🔥 over + ball parse
    let parts = overText.split(".");
    let over = parseInt(parts[0]) || 0;
    let ball = parseInt(parts[1]) || 0;

    let totalOvers = over + (ball / 6);

    let crr = 0;

    if(totalOvers > 0){
        crr = (score / totalOvers).toFixed(2);
    }

    document.getElementById("crr").innerText = crr;
}
function updateRRR(){

    let innings = document.getElementById("inningsData")?.innerText.trim();
    if(innings != "2") return;

    let scoreText = document.getElementById("score").innerText;
    let overText = document.getElementById("over").innerText;

    let score = parseInt(scoreText.split(" - ")[0]) || 0;

    let parts = overText.split(".");
    let over = parseInt(parts[0]) || 0;
    let ball = parseInt(parts[1]) || 0;

    let target = parseInt(document.getElementById("target")?.innerText) || 0;
    let totalOvers = parseInt(document.getElementById("oversData")?.innerText) || 0;

    let ballsPlayed = over * 6 + ball;
    let totalBalls = totalOvers * 6;

    let ballsLeft = totalBalls - ballsPlayed;
    let runsNeeded = target - score;

    let rrr = 0;

    // 🔥 FIXED LOGIC
    if(runsNeeded <= 0){
        rrr = 0;
    }
    else if(ballsLeft <= 0){
        rrr = 0;
    }
    else{
        let oversLeft = ballsLeft / 6;
        rrr = runsNeeded / oversLeft;
    }

    document.getElementById("rrr").innerText = rrr.toFixed(2);
}

function updateNeed(){

    let innings = document.getElementById("inningsData")?.innerText.trim();
    if(innings != "2") return;

    let team = document.querySelector(".live-top span")?.innerText.split(",")[0] || "";

    // 🔥 DOM থেকে data নে
    let scoreText = document.getElementById("score").innerText;
    let overText = document.getElementById("over").innerText;

    let score = parseInt(scoreText.split(" - ")[0]) || 0;

    let parts = overText.split(".");
    let over = parseInt(parts[0]) || 0;
    let ball = parseInt(parts[1]) || 0;

    let target = parseInt(document.getElementById("target")?.innerText) || 0;
    let totalOvers = parseInt(document.getElementById("oversData")?.innerText) || 0;

    let ballsPlayed = over * 6 + ball;
    let totalBalls = totalOvers * 6;

    let ballsLeft = totalBalls - ballsPlayed;
    let runsNeeded = target - score;

    // 🔥 TEXT UPDATE
    document.getElementById("needText").innerText =
        `${team} need ${runsNeeded} runs in ${ballsLeft} balls`;

    
}
let matchEnded = false; // 🔥 GLOBAL (একবারই declare)

function checkMatchResult(){

    if(matchEnded) return; // 🔥 STOP duplicate

    let innings = document.getElementById("inningsData")?.innerText.trim();
    if(innings != "2") return;

    let scoreText = document.getElementById("score").innerText;
    let overText = document.getElementById("over").innerText;

    let score = parseInt(scoreText.split(" - ")[0]) || 0;
    let wickets = parseInt(scoreText.split(" - ")[1]) || 0;

    let parts = overText.split(".");
    let over = parseInt(parts[0]) || 0;
    let ball = parseInt(parts[1]) || 0;

    let target = parseInt(document.getElementById("target")?.innerText) || 0;

    let totalOvers = parseInt(document.getElementById("oversData")?.innerText) || 0;
    let players = parseInt(document.getElementById("playersData")?.innerText) || 11;

    let maxWickets = players - 1;

    let ballsPlayed = over * 6 + ball;
    let totalBalls = totalOvers * 6;

    let battingTeam = document.querySelector(".live-top span")?.innerText.split(",")[0];
    let bowlingTeam = document.getElementById("bowlingTeamData")?.innerText.trim();
    console.log("CHECK RESULT RUNNING:", score, target);

    // 🔥 WIN
    if(score >= target){

        matchEnded = true;

        let wicketsLeft = maxWickets - wickets;
        let resultText = `${battingTeam} won by ${wicketsLeft} wickets`;

        setTimeout(() => {
            fetch("/save-result", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ result: resultText })
            }).then(() => {
                openResult(resultText);
            });
        }, 100);

        return;
    }

    // 🔥 LOSS
    if(wickets >= maxWickets || ballsPlayed >= totalBalls){

        matchEnded = true;

        let runsShort = target - score;
        let resultText = `${bowlingTeam} Win by ${runsShort} runs`;

        setTimeout(() => {
            fetch("/save-result", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ result: resultText })
            }).then(() => {
                openResult(resultText);
            });
        }, 100);

        return;
    }
}

function saveBowler(){

    const bowler = document.getElementById("bowlerName").value;

    if(!bowler.trim()){
        alert("Select bowler");
        return;
    }

    const params = new URLSearchParams(window.location.search);

    const newPlayer = params.get("new");   // only for wicket
    const type = params.get("type");

    let url = "/live-match?bowler=" + encodeURIComponent(bowler);

    // 🔥 ONLY if wicket flow
    if(newPlayer && type){
        url += "&new=" + encodeURIComponent(newPlayer);
        url += "&type=" + encodeURIComponent(type);
        url += "&overEnded=true";
    }

    window.location.href = url;
}

function openExtra(){
    modalOpen = true;
    // 🔥 set values
    document.getElementById("exTotal").innerText = extraTotal;
    document.getElementById("exLB").innerText = extraLB;
    document.getElementById("exB").innerText = extraB;
    document.getElementById("exWD").innerText = extraWD;
    document.getElementById("exNB").innerText = extraNB;

    document.getElementById("extraModal").classList.add("show");
}

function closeExtra(){
    modalOpen = false;
    document.getElementById("extraModal").classList.remove("show");
}

// 🔥 click outside close (same as manage team)
window.addEventListener("click", function(e){
    const modal = document.getElementById("extraModal");
    if(e.target === modal){
        modal.classList.remove("show");
    }
});

function openUndo(){
    document.getElementById("undoModal").classList.add("show");
}

function closeUndo(){
    document.getElementById("undoModal").classList.remove("show");
}

function confirmUndo(){
    window.location.href = "/undo";
}

function renderPartnerships(){

    let container = document.getElementById("partnerList");
    container.innerHTML = "";

    partnerships.forEach(p => {

        let percent = Math.min((p.runs / 100) * 100, 100);

        container.innerHTML += `
        <div style="margin-bottom:15px;">
            
            <div style="display:flex; justify-content:space-between;">
                <span>${p.striker}</span>
                <span><b>${p.runs} (${p.balls})</b></span>
                <span>${p.nonStriker}</span>
            </div>

            <div style="height:6px; background:#333; margin-top:5px; border-radius:5px;">
                <div style="
                    width:${percent}%;
                    height:100%;
                    background:#4da6ff;
                    border-radius:5px;
                "></div>
            </div>

        </div>
        `;
    });
}

function openPartner(){
    modalOpen = true;
    renderPartnerships();
    document.getElementById("partnerModal").classList.add("show");
}

function closePartner(){
    modalOpen = false;
    document.getElementById("partnerModal").classList.remove("show");
}


function openInningsModal(target, overs){

    let rrr = (target / overs).toFixed(2);

    document.getElementById("targetText").innerText =
        `Need ${target} runs in ${overs} overs`;

    document.getElementById("rrrText").innerText =
        `Required Run Rate: ${rrr}`;

    document.getElementById("inningsModal").style.display = "flex";
}

function closeInnings(){
    document.getElementById("inningsModal").style.display = "none";
}

function startSecond(){
    window.location.href = "/start-second";
}

function openResult(text){
    document.getElementById("resultText").innerText = text;
    document.getElementById("resultModal").classList.add("show");
}

function closeResult(){
    document.getElementById("resultModal").classList.remove("show");
}

function goNewMatch(){
    window.location.href = "/new-match";
}
function checkMatchResultDirect(score, wickets, over, ball){

    if(matchEnded) return true;

    let target = parseInt(document.getElementById("target")?.innerText) || 0;
    let totalOvers = parseInt(document.getElementById("oversData")?.innerText) || 0;
    let players = parseInt(document.getElementById("playersData")?.innerText) || 11;

    let maxWickets = players - 1;

    let ballsPlayed = over * 6 + ball;
    let totalBalls = totalOvers * 6;

    let battingTeam = document.querySelector(".live-top span")?.innerText.split(",")[0];
    let bowlingTeam = document.getElementById("bowlingTeamData")?.innerText.trim();

    // 🔥 WIN
    if(score >= target){
        matchEnded = true;

        let wicketsLeft = maxWickets - wickets;
        let resultText = `${battingTeam} won by ${wicketsLeft} wickets`;

        fetch("/save-result", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ result: resultText })
        }).then(() => openResult(resultText));

        return true;
    }

    // 🔥 LOSS
    if(wickets >= maxWickets || ballsPlayed >= totalBalls){
        matchEnded = true;
        
        // 🔥 DRAW CONDITION (ADD ONLY THIS PART)
        if(score === target - 1){
            let resultText = `Match Draw(Running super over)`;

            fetch("/save-result", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ result: resultText })
            }).then(() => openResult(resultText));

            return true;
        }

        let runsShort = (target - score)-1;
        let resultText = `${bowlingTeam} Win by ${runsShort} runs`;

        fetch("/save-result", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ result: resultText })
        }).then(() => openResult(resultText));

        return true;
    }

    return false;
}

function syncPartnershipFromDOM(){

    let pData = document.getElementById("partnerData")?.textContent.trim();

    if(pData){
        try{
            partnerships = JSON.parse(pData);
        }catch(e){
            partnerships = [];
        }
    }
}