// Obtener el token de seguridad desde las propiedades del script
function getSecureToken() {
  var scriptProperties = PropertiesService.getScriptProperties();
  return scriptProperties.getProperty('SECURE_TOKEN');
}

function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  
  // Check action type
  if (data.action === 'sendEmail') {
    return handleSendEmail(data);
  }
  
  // Continue with existing file/folder handling
  if (data.token !== getSecureToken()) {
    return ContentService.createTextOutput(JSON.stringify({
      'error': 'Token inválido'
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  try {
    // Obtener la carpeta raíz donde se guardarán los archivos
    var parentFolder = DriveApp.getRootFolder();
    if (data.parentFolderId) {
      parentFolder = DriveApp.getFolderById(data.parentFolderId);
    }
    
    // Crear una nueva carpeta con apellido + fecha
    var newFolder = parentFolder.createFolder(data.folderName);
    
    // Si hay un PDF para guardar
    var fileId = null;
    if (data.pdfContent) {
      var decodedPdf = Utilities.base64Decode(data.pdfContent);
      var pdfBlob = Utilities.newBlob(decodedPdf, 'application/pdf', data.fileName);
      var file = newFolder.createFile(pdfBlob);
      fileId = file.getId();
    }
    
    // Retornar la información de la carpeta creada
    return ContentService.createTextOutput(JSON.stringify({
      'success': true,
      'folderId': newFolder.getId(),
      'folderUrl': newFolder.getUrl(),
      'fileId': fileId
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      'error': error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function createSpreadsheet(data) {
  // Verificar el token de seguridad
  if (data.token !== getSecureToken()) {
    return {
      'error': 'Token inválido'
    };
  }
  
  try {
    var spreadsheet = SpreadsheetApp.create(data.spreadsheetName);
    var sheet = spreadsheet.getActiveSheet();
    
    // Agregar encabezados
    if (data.headers && data.headers.length > 0) {
      sheet.getRange(1, 1, 1, data.headers.length).setValues([data.headers]);
    }
    
    // Agregar datos
    if (data.rows && data.rows.length > 0) {
      sheet.getRange(2, 1, data.rows.length, data.headers.length).setValues(data.rows);
    }
    
    return {
      'success': true,
      'spreadsheetId': spreadsheet.getId(),
      'spreadsheetUrl': spreadsheet.getUrl()
    };
    
  } catch (error) {
    return {
      'error': error.toString()
    };
  }
}

function sendEmail(to, subject, htmlBody, senderName = null, attachmentIds = [], placeholders = null) {
  // Process placeholders if provided
  if (placeholders) {
    subject = replacePlaceholders(subject, placeholders);
    htmlBody = replacePlaceholders(htmlBody, placeholders);
  }

  const emailOptions = {
    to: to,
    subject: subject,
    htmlBody: htmlBody,
    name: senderName || 'Estación Biológica de Puerto Blest'
  };

  if (attachmentIds && attachmentIds.length > 0) {
    emailOptions.attachments = attachmentIds.map(id => DriveApp.getFileById(id));
  }

  try {
    GmailApp.sendEmail(to, subject, '', emailOptions);
    return {
      success: true,
      message: `Email sent successfully to ${to}`
    };
  } catch (error) {
    throw new Error(`Failed to send email: ${error.message}`);
  }
}

function handleSendEmail(data) {
  if (!data.token || data.token !== getSecureToken()) {
    return createErrorResponse('Token inválido');
  }

  if (!data.to || !data.subject || !data.htmlBody) {
    return createErrorResponse('Recipient, subject, and HTML body are required.');
  }
  
  try {
    const result = sendEmail(
      data.to,
      data.subject,
      data.htmlBody,
      data.senderName,
      data.attachmentIds,
      data.placeholders
    );
    
    return createSuccessResponse(result);
  } catch (error) {
    return createErrorResponse(error.message);
  }
}

function replacePlaceholders(text, placeholders) {
  if (!text || !placeholders) return text;
  
  return Object.entries(placeholders).reduce((result, [key, value]) => {
    const regex = new RegExp(`<<${key}>>`, 'g');
    return result.replace(regex, value);
  }, text);
}

function createSuccessResponse(data) {
  return ContentService.createTextOutput(JSON.stringify({
    'success': true,
    'result': data
  })).setMimeType(ContentService.MimeType.JSON);
}

function createErrorResponse(message) {
  return ContentService.createTextOutput(JSON.stringify({
    'success': false,
    'error': message
  })).setMimeType(ContentService.MimeType.JSON);
}

function setupTrigger() {
  // Create a trigger that runs when a form is submitted
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onFormSubmit()
    .create();
}