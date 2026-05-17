// ── Dashboard interactions

document.addEventListener("DOMContentLoaded", function () {
  const readAllBtn = document.getElementById("read-all-btn");
  if (readAllBtn) {
    readAllBtn.addEventListener("click", function () {
      // Get CSRF token from cookie
      function getCookie(name) {
        var v = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
        return v ? decodeURIComponent(v[2]) : null;
      }

      fetch("/dashboard/mark-all-read/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          if (data.status === "ok") {
            document
              .querySelectorAll("#widget-notifications .dot")
              .forEach(function (dot) {
                dot.remove();
              });
            const badge = document.getElementById("notif-badge");
            if (badge) {
              badge.textContent = "0";
              badge.style.background = "#94a3b8";
            }
          }
        })
        .catch(function (err) {
          console.error("mark-all-read failed:", err);
        });
    });
  }

  const PREVIEW_COUNT = 5;

  document.querySelectorAll(".view-all").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const target = btn.getAttribute("data-target");
      const list = document.getElementById("list-" + target);
      if (!list) return;

      const items = list.querySelectorAll(".activity-item");
      const expanded = btn.getAttribute("data-expanded") === "true";

      if (expanded) {
        items.forEach(function (item, i) {
          item.style.display = i < PREVIEW_COUNT ? "" : "none";
        });
        btn.textContent = "View all";
        btn.setAttribute("data-expanded", "false");
      } else {
        items.forEach(function (item) {
          item.style.display = "";
        });
        btn.textContent = "Show less";
        btn.setAttribute("data-expanded", "true");
      }
    });

    const target = btn.getAttribute("data-target");
    const list = document.getElementById("list-" + target);
    if (list) {
      const items = list.querySelectorAll(".activity-item");
      items.forEach(function (item, i) {
        if (i >= PREVIEW_COUNT) item.style.display = "none";
      });
      btn.setAttribute("data-expanded", "false");
    }
  });

  document.querySelectorAll(".js-refresh").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const icon = btn.querySelector("i");
      if (icon) {
        icon.style.transition = "transform 0.5s";
        icon.style.transform = "rotate(360deg)";
        setTimeout(function () {
          icon.style.transform = "";
        }, 500);
      }
      window.location.reload();
    });
  });

  document.querySelectorAll(".js-filter").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-target");
      alert('Filter for "' + target + '" coming soon.');
    });
  });

  document.querySelectorAll(".js-export").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-target");
      const list = document.getElementById("list-" + target);
      if (!list) return;

      const rows = [["Actor", "Action", "Item", "Timestamp"]];
      list.querySelectorAll(".activity-item").forEach(function (item) {
        const text = item.querySelector(".activity-text");
        const meta = item.querySelector(".activity-meta");
        const strongs = text ? text.querySelectorAll("strong") : [];
        const actor = strongs[0] ? strongs[0].textContent.trim() : "";
        const itemLabel = strongs[1] ? strongs[1].textContent.trim() : "";
        const actionRaw = text
          ? text.textContent.replace(actor, "").replace(itemLabel, "").trim()
          : "";
        const timestamp = meta ? meta.textContent.trim() : "";
        rows.push([actor, actionRaw, itemLabel, timestamp]);
      });

      const csv = rows
        .map(function (r) {
          return r
            .map(function (c) {
              return '"' + c.replace(/"/g, '""') + '"';
            })
            .join(",");
        })
        .join("\n");

      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = target + "_export.csv";
      a.click();
      URL.revokeObjectURL(url);
    });
  });
});
