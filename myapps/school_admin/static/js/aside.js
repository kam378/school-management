document.addEventListener("DOMContentLoaded", () => {
  const aside = document.querySelector("aside");
  const main = document.querySelector("main");
  const bars = document.querySelector(".bars-header");
  const close = document.querySelector(".close-icon");
  const root = document.documentElement;
  const slide_bars = document.getElementById("slide-aside-bars")

  asideCheck();

  function asideCheck() {
    const isCollapsed = localStorage.getItem("aside") === "true";
    const profile_info = document.querySelector(".profile-info");
    const profile_icon = document.querySelector(".user_icon");
    const link_name = document.querySelectorAll(".link-name");

    if (isCollapsed) {
      aside.style.width = "5%";
      main.style.width = "95%";
      profile_info.style.display = "none";
      profile_icon.style.fontSize = "20px";
      profile_icon.style.fontSize = "20px"
      link_name.forEach(elem => {
        elem.style.display = "none";
      });
    } else {
      aside.style.width = "18%";
      main.style.width = "82%";
      profile_info.style.display = "initial";
      profile_icon.style.fontSize = "40px";
      link_name.forEach(elem => {
        elem.style.display = "flex";
      });
    }
  }

  bars.addEventListener("click", () => {
    const isCollapsed = localStorage.getItem("aside") === "true";
    localStorage.setItem("aside", (!isCollapsed).toString());
    asideCheck();
  });

  slide_bars.addEventListener("click", () => {
    aside.style.left = "0%"
  })

  close.addEventListener("click", () => {
    aside.style.left = "-80%"
  })
        
});