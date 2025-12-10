/**
 * Local storage service for saving customer data to JSON files
 * This saves data to a local folder on the user's PC
 */

/**
 * Save company data to local JSON file
 * @param {string} companyId - Unique company identifier
 * @param {object} companyData - Company data object
 * @returns {Promise<{success: boolean, message: string, filePath?: string}>}
 */
export const saveCompanyDataLocally = async (companyId, companyData) => {
  try {
    // Create a JSON blob
    const jsonData = JSON.stringify(companyData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${companyId}.json`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    // Also save to localStorage as backup
    localStorage.setItem(`techscope_company_${companyId}`, jsonData);
    
    return {
      success: true,
      message: 'Company data saved successfully',
      filePath: `${companyId}.json`
    };
  } catch (error) {
    console.error('Error saving company data locally:', error);
    return {
      success: false,
      message: `Error saving data: ${error.message}`
    };
  }
};

/**
 * Save company data to a specific folder (requires user interaction)
 * This will prompt the user to select a folder and save the file there
 */
export const saveCompanyDataToFolder = async (companyId, companyData) => {
  try {
    // Check if File System Access API is available (Chrome/Edge)
    if ('showSaveFilePicker' in window) {
      try {
        const fileHandle = await window.showSaveFilePicker({
          suggestedName: `${companyId}.json`,
          types: [{
            description: 'JSON files',
            accept: { 'application/json': ['.json'] }
          }]
        });
        
        const writable = await fileHandle.createWritable();
        const jsonData = JSON.stringify(companyData, null, 2);
        await writable.write(jsonData);
        await writable.close();
        
        return {
          success: true,
          message: 'Company data saved successfully',
          filePath: fileHandle.name
        };
      } catch (error) {
        // User cancelled or error occurred
        if (error.name !== 'AbortError') {
          console.error('Error with File System Access API:', error);
        }
        // Fallback to download method
        return await saveCompanyDataLocally(companyId, companyData);
      }
    } else {
      // Fallback: use download method
      return await saveCompanyDataLocally(companyId, companyData);
    }
  } catch (error) {
    console.error('Error saving company data:', error);
    return {
      success: false,
      message: `Error saving data: ${error.message}`
    };
  }
};

/**
 * Load company data from localStorage
 * @param {string} companyId - Company identifier
 * @returns {object|null} Company data or null if not found
 */
export const loadCompanyDataFromLocal = (companyId) => {
  try {
    const data = localStorage.getItem(`techscope_company_${companyId}`);
    if (data) {
      return JSON.parse(data);
    }
    return null;
  } catch (error) {
    console.error('Error loading company data from local storage:', error);
    return null;
  }
};

