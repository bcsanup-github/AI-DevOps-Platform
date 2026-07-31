const button=document.getElementById("sendButton");

button.onclick=async()=>{

const prompt=document.getElementById("prompt").value;

const response=await fetch("/chat",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({

prompt:prompt

})

});

const data=await response.json();

document.getElementById("chatBox").innerHTML=`

<b>You</b>

<p>${prompt}</p>

<hr>

<b>AI</b>

<p>${data.response}</p>

`;

}