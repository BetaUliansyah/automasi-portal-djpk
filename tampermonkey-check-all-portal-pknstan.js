// ==UserScript==
// @name         Check All 'Yes' Radios with Button
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Adds a button to check all radio buttons with class 'yes' on rekamkul page
// @author       Beta
// @match        https://portal.pknstan.ac.id/lect/jdpjj/rekamkul/*
// @icon         https://portal.pknstan.ac.id/assets/plugins/images/stan_ico.ico
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function checkAllYesRadios() {
        const radios = document.getElementsByClassName('yes');
        for (let i = 0; i < radios.length; i++) {
            if (radios[i].type === 'radio') {
                radios[i].checked = true;
            }
        }
    }

    function createCheckAllButton() {
        const button = document.createElement('button');
        button.textContent = '✔ Check All Yes';
        button.style.position = 'fixed';
        button.style.top = '20px';
        button.style.right = '20px';
        button.style.zIndex = '9999';
        button.style.padding = '10px 15px';
        button.style.backgroundColor = '#28a745';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '6px';
        button.style.cursor = 'pointer';
        button.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
        button.onclick = checkAllYesRadios;

        document.body.appendChild(button);
    }

    window.addEventListener('load', createCheckAllButton);
})();
