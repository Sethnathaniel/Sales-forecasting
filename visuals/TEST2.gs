// ==========================================
// CONFIGURATION
// ==========================================
const GITHUB_TOKEN = "ghp_2QjLUn3ZdxzcDzczcDzddDI96ob"; // À remplacer par ton token GitHub

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('SecMind - Shield & DPO Marketplace')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// ==========================================
// LOGIQUE D'AUTHENTIFICATION COMPATIBLE CASSE
// ==========================================
function loginUser(email, password) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Membres");
  const data = sheet.getDataRange().getValues();
  
  const cleanEmail = email.trim().toLowerCase();
  const cleanPassword = password.trim();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] && data[i][1]) {
      const sheetEmail = data[i][0].toString().trim().toLowerCase();
      const sheetPassword = data[i][1].toString().trim();
      let sheetRole = data[i][2] ? data[i][2].toString().trim() : "Client";
      
      sheetRole = sheetRole.charAt(0).toUpperCase() + sheetRole.slice(1).toLowerCase();

      if (sheetEmail === cleanEmail && sheetPassword === cleanPassword) {
        return { success: true, email: sheetEmail, role: sheetRole };
      }
    }
  }
  return { success: false, message: "Identifiants incorrects." };
}

function registerUser(email, password, role) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Membres");
  sheet.appendRow([email.trim().toLowerCase(), password.trim(), role.trim()]);
  return { success: true };
}

// ==========================================
// ENREGISTREMENT ET PORTES CLIENTS PME
// ==========================================
function getDpoClients(dpoEmail) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Clients");
  const data = sheet.getDataRange().getValues();
  let clients = [];
  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toLowerCase() === dpoEmail.toLowerCase()) {
      clients.push({ name: data[i][1], repo: data[i][2] });
    }
  }
  return clients;
}

function addClient(userEmail, clientName, repoUrl) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Clients");
  sheet.appendRow([userEmail.trim().toLowerCase(), clientName.trim(), repoUrl.trim()]);
  return { success: true };
}

// ==========================================
// MOTEUR DE SCAN CYBER & AUTOMATION EMAIL
// ==========================================
function runAudit(clientName, repoUrl, userEmail) {
  try {
    const urlParts = repoUrl.replace("https://github.com/", "").replace(".git","").split("/");
    const owner = urlParts[0];
    const repo = urlParts[1];
    
    let treeUrl = `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`;
    let options = {
      "headers": { "Authorization": "token " + GITHUB_TOKEN },
      "muteHttpExceptions": true
    };
    
    let response = UrlFetchApp.fetch(treeUrl, options);
    if (response.getResponseCode() === 404) {
      treeUrl = `https://api.github.com/repos/${owner}/${repo}/git/trees/master?recursive=1`;
      response = UrlFetchApp.fetch(treeUrl, options);
    }
    
    if (response.getResponseCode() !== 200) {
      return { success: false, error: "Dépôt introuvable ou privé. Vérifiez votre configuration." };
    }
    
    const treeData = JSON.parse(response.getContentText());
    let vulnerabilities = [];
    const scanSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scans");
    const today = new Date().toLocaleDateString();
    
    let fileCount = 0;
    for (let file of treeData.tree) {
      if (file.type === "blob" && (file.path.endsWith(".js") || file.path.endsWith(".py") || file.path.endsWith(".env") || file.path.endsWith(".json") || file.path.endsWith(".ipynb"))) {
        if (fileCount > 5) break; 
        
        const fileUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${file.path}`;
        const fileResp = UrlFetchApp.fetch(fileUrl, {
          "headers": { "Authorization": "token " + GITHUB_TOKEN, "Accept": "application/vnd.github.v3.raw" }
        });
        
        const content = fileResp.getContentText();
        const regexRules = {
          "Clé d'API AWS générique": /AKIA[0-9A-Z]{16}/g,
          "Clé Secrète ou Password Exposé": /(password|passwd|secret|api_key|token)\s*=\s*['"][a-zA-Z0-9_\-]{10,}['"]/gi
        };
        
        for (let [ruleName, regex] of Object.entries(regexRules)) {
          if (regex.test(content)) {
            // Note : On stocke l'email de l'utilisateur dans la colonne 1 pour filtrer son historique
            scanSheet.appendRow([userEmail.toLowerCase(), today, "⚠️ Alerte", file.path, `Entreprise: ${clientName} - Détection : ${ruleName}`]);
            vulnerabilities.push({ file: file.path, type: ruleName });
          }
        }
        fileCount++;
      }
    }
    
    let statusText = vulnerabilities.length > 0 ? "⚠️ Alerte" : "✅ Clean";
    if (vulnerabilities.length === 0) {
      scanSheet.appendRow([userEmail.toLowerCase(), today, "✅ Clean", "Aucun", `Entreprise: ${clientName} - Aucune clé exposée détectée.`]);
    }
    
    // Si l'utilisateur est connecté, on lui envoie son rapport texte/mail automatique
    if (userEmail) {
      envoyerRapportEmail(userEmail, clientName, repoUrl, statusText, vulnerabilities);
    }
    
    return { success: true, vulnerabilities: vulnerabilities.length };
    
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

function envoyerRapportEmail(email, clientName, repo, status, vulnerabilities) {
  let subject = `[SecMind Shield] Rapport d'Audit Automatique - ${clientName}`;
  let body = `Bonjour,\n\nLe scanner automatique SecMind s'est déclenché suite à une modification (commit) sur votre dépôt (${repo}).\n\n`;
  body += `Statut Global de Conformité : ${status}\n`;
  body += `Nombre de secrets critiques exposés : ${vulnerabilities.length}\n\n`;
  
  if (vulnerabilities.length > 0) {
    body += `Détails des vulnérabilités trouvées dans le code source :\n`;
    vulnerabilities.forEach(v => {
      body += `- Fichier impacté : ${v.file} | Alerte : ${v.type}\n`;
    });
    body += `\n⚠️ ATTENTION : Ces informations sont critiques, veuillez révoquer vos clés d'API au plus vite.`;
  } else {
    body += `Félicitations, vos fichiers de production sont propres. Aucun mot de passe ni token n'a été laissé en clair.`;
  }
  body += `\n\nL'équipe SecMind - Sécurité Automatisée.`;
  MailApp.sendEmail(email, subject, body);
}

// SIMULATEUR DE WEBHOOK / ACTIONS COMMITS
function triggerWebhookSimulation(clientEmail) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const clientSheet = ss.getSheetByName("Clients");
  const data = clientSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toLowerCase() === clientEmail.toLowerCase()) {
      return runAudit(data[i][1], data[i][2], clientEmail);
    }
  }
  return { success: false, error: "Aucun dépôt lié à votre compte. Enregistrez un dépôt GitHub d'abord !" };
}

// HISTORIQUE TECHNIQUE ULTRA-RAPIDE MULTI-RÔLE
function getScanHistory(identifier) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scans");
  const data = sheet.getDataRange().getValues();
  let history = [];
  const cleanId = identifier.toLowerCase().trim();
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toLowerCase().trim() === cleanId) {
      history.push({ date: data[i][1], status: data[i][2], file: data[i][3], details: data[i][4] });
    }
  }
  return history.reverse(); // Plus récent en premier
}

// ==========================================
// MARKETPLACE DE CONSULTING DPO & VEILLE
// ==========================================
function getDpoList() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Membres");
  const data = sheet.getDataRange().getValues();
  let dpos = [];
  for (let i = 1; i < data.length; i++) {
    if (data[i][2].toString().toLowerCase() === "dpo") { dpos.push(data[i][0]); }
  }
  return dpos;
}

function bookAppointment(clientEmail, dpoEmail, dateSlot, typeAudit) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scans");
  const today = new Date().toLocaleDateString();
  sheet.appendRow([clientEmail.toLowerCase(), today, "📅 Rdv Fixé", typeAudit, `Consultation planifiée le ${dateSlot} avec l'expert DPO : ${dpoEmail}`]);
  return { success: true };
}

function getVeilleReglementaire() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Veille");
  const data = sheet.getDataRange().getValues();
  let updates = [];
  for (let i = 1; i < data.length; i++) { updates.push({ date: data[i][0], type: data[i][1], description: data[i][2] }); }
  return updates.reverse();
}

function addVeilleLog(type, description) {
  SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Veille").appendRow([new Date().toLocaleDateString(), type, description]);
  return { success: true };
}

function getAdminDashboardData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const totalUsers = ss.getSheetByName("Membres").getLastRow() - 1;
  const totalClients = ss.getSheetByName("Clients").getLastRow() - 1;
  const totalScans = ss.getSheetByName("Scans").getLastRow() - 1;
  const membresData = ss.getSheetByName("Membres").getDataRange().getValues();
  let userList = [];
  for(let i = 1; i < membresData.length; i++) { userList.push({ email: membresData[i][0], role: membresData[i][2] }); }
  return { stats: { users: totalUsers, clients: totalClients, scans: totalScans }, users: userList };
}
