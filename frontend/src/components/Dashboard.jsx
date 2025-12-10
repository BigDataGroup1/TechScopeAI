import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  pitchAPI, 
  competitiveAPI, 
  marketingAPI, 
  policyAPI, 
  patentAPI, 
  teamAPI, 
  chatAPI,
  questionnaireAPI
} from '../services/api';
import AgentForm from './AgentForm';
import jsPDF from 'jspdf';
import { stripMarkdown } from '../utils/markdown';

const Dashboard = ({ companyId, companyData }) => {
  const [loading, setLoading] = useState({});
  const [results, setResults] = useState({});
  const [activities, setActivities] = useState([]);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [showPPTPreview, setShowPPTPreview] = useState(false);
  const [previewSlides, setPreviewSlides] = useState(null);
  const [expandedActivityId, setExpandedActivityId] = useState(null);
  
  // Form states
  const [showForm, setShowForm] = useState(false);
  const [formType, setFormType] = useState(null); // 'patent', 'marketing', 'policy', 'team'
  
  // Prompt states for all agents
  const [marketingPrompt, setMarketingPrompt] = useState('');
  const [showMarketingPrompt, setShowMarketingPrompt] = useState(false);
  const [patentPrompt, setPatentPrompt] = useState('');
  const [showPatentPrompt, setShowPatentPrompt] = useState(false);
  const [policyPrompt, setPolicyPrompt] = useState('');
  const [showPolicyPrompt, setShowPolicyPrompt] = useState(false);
  const [policyType, setPolicyType] = useState('privacy'); // 'privacy' or 'terms'
  const [teamPrompt, setTeamPrompt] = useState('');
  const [showTeamPrompt, setShowTeamPrompt] = useState(false);
  const [jobDescPrompt, setJobDescPrompt] = useState('');
  const [showJobDescPrompt, setShowJobDescPrompt] = useState(false);
  const [formQuestionnaire, setFormQuestionnaire] = useState([]);
  const [formTitle, setFormTitle] = useState('');

  const handleDownloadReport = async () => {
    if (activities.length === 0) {
      alert('No activities to download');
      return;
    }

    const companyName = companyData?.basic_info?.company_name || companyData?.companyName || 'Your Company';
    const reportDate = new Date().toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });

    // Create PDF document
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    let yPosition = 20;
    const margin = 20;
    const lineHeight = 7;
    const sectionSpacing = 10;
    
    // Helper function to load image and add to PDF
    const addImageToPDF = (imageUrl, doc, x, y, maxWidth, maxHeight) => {
      return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        img.onload = () => {
          try {
            // Calculate dimensions to fit within maxWidth and maxHeight
            let width = img.width;
            let height = img.height;
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width = width * ratio;
            height = height * ratio;
            
            // Convert image to base64 data URL
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            const imgData = canvas.toDataURL('image/png');
            
            // Add image to PDF
            doc.addImage(imgData, 'PNG', x, y, width, height);
            resolve(height);
          } catch (error) {
            console.error('Error adding image to PDF:', error);
            resolve(0);
          }
        };
        
        img.onerror = () => {
          console.error('Error loading image:', imageUrl);
          resolve(0);
        };
        
        img.src = imageUrl;
      });
    };

    // Helper function to add new page if needed
    const checkPageBreak = (requiredSpace = 20) => {
      if (yPosition + requiredSpace > pageHeight - margin) {
        doc.addPage();
        yPosition = 20;
        return true;
      }
      return false;
    };

    // Helper function to add text with word wrap
    const addText = (text, fontSize = 10, isBold = false, color = [0, 0, 0]) => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');
      doc.setTextColor(color[0], color[1], color[2]);
      
      const maxWidth = pageWidth - (margin * 2);
      const lines = doc.splitTextToSize(text, maxWidth);
      
      checkPageBreak(lines.length * lineHeight);
      
      lines.forEach((line) => {
        if (yPosition > pageHeight - margin - lineHeight) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(line, margin, yPosition);
        yPosition += lineHeight;
      });
    };

    // Header
    doc.setFillColor(99, 102, 241); // Indigo
    doc.rect(0, 0, pageWidth, 40, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('TechScopeAI Activity Report', margin, 25);
    
    yPosition = 50;

    // Company Info
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('Company Information', margin, yPosition);
    yPosition += lineHeight;
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Company: ${companyName}`, margin, yPosition);
    yPosition += lineHeight;
    doc.text(`Report Generated: ${reportDate}`, margin, yPosition);
    yPosition += lineHeight;
    doc.text(`Total Activities: ${activities.length}`, margin, yPosition);
    yPosition += sectionSpacing * 2;

    // Activities (process sequentially to handle async image loading)
    for (let index = 0; index < activities.length; index++) {
      const activity = activities[index];
      checkPageBreak(30);
      
      // Activity number and title
      doc.setFillColor(139, 92, 246); // Purple
      doc.rect(margin - 5, yPosition - 8, pageWidth - (margin * 2) + 10, 8, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text(`${index + 1}. ${activity.title}`, margin, yPosition);
      yPosition += lineHeight + 3;

      // Activity details
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      
      // Date
      doc.text(`Date: ${activity.timestamp}`, margin, yPosition);
      yPosition += lineHeight;

      // Status
      let statusText = '📝 Pending Review';
      let statusColor = [100, 100, 100];
      if (activity.status === 'approved') {
        statusText = '✅ Approved (Liked)';
        statusColor = [34, 197, 94]; // Green
      } else if (activity.status === 'needs_changes') {
        statusText = '⚠️ Needs Changes';
        statusColor = [239, 68, 68]; // Red
      }
      
      doc.setTextColor(statusColor[0], statusColor[1], statusColor[2]);
      doc.setFont('helvetica', 'bold');
      doc.text(`Status: ${statusText}`, margin, yPosition);
      yPosition += lineHeight;

      if (activity.modified) {
        doc.setTextColor(234, 179, 8); // Yellow
        doc.text('Modified: Yes', margin, yPosition);
        yPosition += lineHeight;
      }

      doc.setTextColor(0, 0, 0);
      doc.setFont('helvetica', 'normal');

      // Generated Content
      if (activity.content) {
        yPosition += 3;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.text('Generated Content:', margin, yPosition);
        yPosition += lineHeight;
        
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        // Strip markdown for PDF
        const cleanContent = stripMarkdown(activity.content);
        addText(cleanContent, 9, false, [60, 60, 60]);
        yPosition += 3;
      }

      // Images (for Marketing activities)
      if (activity.type === 'marketing' && activity.data) {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        
        // Extract image URLs from multiple possible locations
        let imageUrls = activity.data?.imageUrls || 
                        (activity.data?.results && activity.data.results.flatMap(r => {
                          const imageUrl = r.data?.image_url || 
                                          r.data?.imageUrl || 
                                          (r.data?.response && r.data.response.image_url) ||
                                          r.image_url;
                          
                          if (imageUrl) {
                            let url = imageUrl;
                            if (url && url.startsWith('/')) {
                              url = `${API_BASE_URL}${url}`;
                            }
                            if (url && !url.startsWith('http')) {
                              url = `${API_BASE_URL}${url.startsWith('/') ? url : '/' + url}`;
                            }
                            return [{
                              platform: r.platform || 'Marketing',
                              url: url
                            }];
                          }
                          return [];
                        }));

        if (imageUrls && Array.isArray(imageUrls) && imageUrls.length > 0) {
          yPosition += 3;
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.setTextColor(99, 102, 241); // Indigo
          doc.text('Images:', margin, yPosition);
          yPosition += lineHeight;
          
          // Add each image to PDF
          for (const img of imageUrls) {
            checkPageBreak(80); // Reserve space for image
            
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(0, 0, 0);
            doc.text(`${img.platform} Image:`, margin, yPosition);
            yPosition += lineHeight;
            
            try {
              // Add image to PDF (max width: page width - 2*margin, max height: 60)
              const imageHeight = await addImageToPDF(img.url, doc, margin, yPosition, pageWidth - (margin * 2), 60);
              if (imageHeight > 0) {
                yPosition += imageHeight + 5;
              } else {
                // If image failed to load, add URL as text
                doc.setFontSize(8);
                doc.setTextColor(100, 100, 100);
                doc.text(`Image URL: ${img.url}`, margin, yPosition);
                yPosition += lineHeight;
              }
            } catch (error) {
              console.error('Error adding image to PDF:', error);
              // Add URL as text if image fails
              doc.setFontSize(8);
              doc.setTextColor(100, 100, 100);
              doc.text(`Image URL: ${img.url}`, margin, yPosition);
              yPosition += lineHeight;
            }
            
            yPosition += 3;
          }
        }
      }

      // Modification Request
      if (activity.modification) {
        yPosition += 3;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(234, 179, 8); // Yellow
        doc.text('Modification Request:', margin, yPosition);
        yPosition += lineHeight;
        
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(0, 0, 0);
        addText(activity.modification, 9);
        yPosition += 3;
      }

      // Modification Response
      if (activity.modificationResponse) {
        yPosition += 3;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(34, 197, 94); // Green
        doc.text('Modification Response:', margin, yPosition);
        yPosition += lineHeight;
        
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(0, 0, 0);
        // Strip markdown for PDF
        const cleanModificationResponse = stripMarkdown(activity.modificationResponse);
        addText(cleanModificationResponse, 9);
        yPosition += 3;
      }

      // Additional Data
      if (activity.data) {
        const dataStr = typeof activity.data === 'object' 
          ? JSON.stringify(activity.data, null, 2) 
          : String(activity.data);
        if (dataStr && dataStr.length < 500) {
          yPosition += 3;
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.text('Additional Data:', margin, yPosition);
          yPosition += lineHeight;
          
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(9);
          doc.setTextColor(100, 100, 100);
          addText(dataStr, 9);
        }
      }

      // Separator line
      yPosition += sectionSpacing;
      doc.setDrawColor(200, 200, 200);
      doc.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += sectionSpacing;
    }

    // Footer
    checkPageBreak(20);
    yPosition += 5;
    doc.setDrawColor(200, 200, 200);
    doc.line(margin, yPosition, pageWidth - margin, yPosition);
    yPosition += sectionSpacing;
    
    doc.setFontSize(9);
    doc.setTextColor(100, 100, 100);
    doc.setFont('helvetica', 'italic');
    doc.text('Generated by TechScopeAI - Your AI-Powered Startup Toolkit', margin, yPosition);
    yPosition += lineHeight;
    doc.text('End of Report', margin, yPosition);

    // Save the PDF
    const fileName = `TechScopeAI_Report_${companyName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);
  };

  const addActivity = (type, title, data, content = null, isModification = false, previousContent = null) => {
    const activity = {
      id: Date.now(),
      type,
      title,
      data,
      content, // Store the actual generated content
      previousContent, // Store previous version if this is a modification
      isModification, // Flag to indicate if this is a modified version
      timestamp: new Date().toLocaleString(),
    };
    setActivities(prev => [activity, ...prev]);
  };

  const updateActivity = (id, updates) => {
    setActivities(prev => prev.map(activity => 
      activity.id === id ? { ...activity, ...updates } : activity
    ));
  };

  const handleActivityStatus = (id, status) => {
    const activity = activities.find(a => a.id === id);
    
    // If clicking "Looks good" on a modified activity, keep current version and remove previous
    if (status === 'approved' && activity && (activity.isModification || activity.modified) && activity.previousContent) {
      updateActivity(id, {
        status: 'approved',
        previousContent: null, // Remove previous version completely
        previousData: null,
        isModification: false,
        modified: false,
        modification: null,
        modificationResponse: null,
        regenerationFailed: false
      });
    } else {
      // Just set the status for non-modified activities
      updateActivity(id, { status });
    }
  };

  const handleGeneratePitchDeck = async () => {
    setLoading(prev => ({ ...prev, pitchDeck: true }));
    try {
      console.log('🚀 Starting pitch deck generation...');
      const response = await pitchAPI.generateSlides(companyData);
      console.log('✅ Pitch deck response:', response);
      console.log('📊 PowerPoint:', response.pptx_path);
      console.log('🎨 Gamma:', response.gamma_presentation);
      
      setResults(prev => ({ ...prev, pitchDeck: response }));
      // Store slides content for preview
      setPreviewSlides(response.slides || []);
      addActivity('pitch-deck', 'Pitch Deck Generated', {
        slides: response.slides?.length || 0,
        hasPowerPoint: !!response.pptx_path,
        hasGamma: !!response.gamma_presentation?.success,
      }, response.slides ? `Generated ${response.slides.length} slides: ${response.slides.map(s => s.title).join(', ')}` : null);
    } catch (error) {
      console.error('Error generating pitch deck:', error);
      alert('Failed to generate pitch deck. Please try again.');
    } finally {
      setLoading(prev => ({ ...prev, pitchDeck: false }));
    }
  };

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(prev => ({ ...prev, chat: true }));

    // Check if user is asking to modify content (before API call)
    const lowerMessage = userMessage.toLowerCase();
    const isModificationRequest = lowerMessage.includes('change') || lowerMessage.includes('modify') || 
                                  lowerMessage.includes('update') || lowerMessage.includes('edit') || 
                                  lowerMessage.includes('revise') || lowerMessage.includes('make it') ||
                                  lowerMessage.includes('improve') || lowerMessage.includes('adjust') ||
                                  lowerMessage.includes('redo') || lowerMessage.includes('regenerate') ||
                                  lowerMessage.includes('make the') || lowerMessage.includes('make this') ||
                                  lowerMessage.includes('enhance') || lowerMessage.includes('better');
    
    console.log('💬 Chat message received:', {
      message: userMessage,
      isModificationRequest,
      activitiesCount: activities.length,
      activitiesWithContent: activities.filter(a => a.content && a.type !== 'chat').length
    });
    
    let assistantResponse = '';
    let chatError = null;
    
    try {
      const response = await chatAPI.sendMessage(userMessage, companyId, companyData);
      assistantResponse = response.response || response.content || JSON.stringify(response);
      setChatMessages(prev => [...prev, { role: 'assistant', content: assistantResponse }]);
    } catch (error) {
      console.error('Error sending chat message:', error);
      chatError = error;
      
      // Show user-friendly error message
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to process your request.';
      const isQuotaError = errorMessage.includes('quota') || errorMessage.includes('429') || errorMessage.includes('insufficient');
      
      const friendlyError = isQuotaError 
        ? '⚠️ API request limit reached. Please try again in a moment. Your modification request has been recorded.'
        : `Sorry, I encountered an error: ${errorMessage}`;
      
      assistantResponse = friendlyError;
      setChatMessages(prev => [...prev, { role: 'assistant', content: friendlyError }]);
    } finally {
      // Handle modification requests even if chat API failed
      if (isModificationRequest) {
        console.log('🔍 Modification request detected. Searching for latest activity...');
        // Find the most recent activity with content (not chat messages)
        const latestActivityWithContent = activities.find(a => a.content && a.type !== 'chat');
        console.log('📋 Found activity:', latestActivityWithContent ? {
          id: latestActivityWithContent.id,
          type: latestActivityWithContent.type,
          title: latestActivityWithContent.title,
          hasContent: !!latestActivityWithContent.content
        } : 'NO ACTIVITY FOUND');
        
        if (latestActivityWithContent) {
          // Store previous content before updating
          const previousContent = latestActivityWithContent.content;
          const previousData = latestActivityWithContent.data;
          const activityType = latestActivityWithContent.type;
          
          // Try to regenerate content based on activity type
          let regenerated = false;
          let newContent = null;
          let newData = null;
          
          try {
            // Build modification context - combine original request with user's modification
            const modificationContext = {
              ...companyData,
              modification_request: userMessage,
              original_content_type: activityType
            };
            
            switch (activityType) {
              case 'marketing':
                // Marketing: Use generateFromPrompt
                // Try to get original prompt from title or use a default
                const originalPrompt = latestActivityWithContent.title.replace('Marketing Content Generated: ', '') || 
                                     latestActivityWithContent.title.replace('Marketing Content Generated', '') ||
                                     'Generate marketing content';
                const modificationPrompt = `${originalPrompt ? `Original request: ${originalPrompt}. ` : ''}${userMessage}. Generate updated marketing content with images.`;
                
                try {
                  console.log('🔄 Calling marketing API for modification:', {
                    modificationPrompt: modificationPrompt.substring(0, 100),
                    activityId: latestActivityWithContent.id
                  });
                  
                  const regenerateResponse = await marketingAPI.generateFromPrompt(modificationPrompt, companyData);
                  
                  console.log('📦 Marketing API response:', {
                    hasResponse: !!regenerateResponse,
                    hasSuccess: !!regenerateResponse?.success,
                    hasResults: !!regenerateResponse?.results,
                    resultsCount: regenerateResponse?.results?.length || 0
                  });
                  
                  if (regenerateResponse && regenerateResponse.success && regenerateResponse.results) {
                    const results = regenerateResponse.results;
                    const imageUrls = [];
                    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                    
                    results.forEach(r => {
                      let imageUrl = r.data.image_url || r.data.imageUrl || (r.data.response && r.data.response.image_url);
                      if (imageUrl && imageUrl.startsWith('/')) {
                        imageUrl = `${API_BASE_URL}${imageUrl}`;
                      }
                      if (imageUrl) {
                        imageUrls.push({
                          platform: r.platform,
                          url: imageUrl,
                          prompt: r.data.image_prompt || r.data.prompt_used || r.data.image_prompt_description
                        });
                      }
                    });
                    
                    newContent = results.map(r => {
                      const content = r.data.content || r.data.posts || r.data.strategies || r.data.response || JSON.stringify(r.data).substring(0, 200);
                      return `**${r.platform}:**\n${content}`;
                    }).join('\n\n');
                    
                    newData = {
                      results: results,
                      imageUrls: imageUrls
                    };
                    regenerated = true;
                  } else {
                    // If regeneration structure is different, still try to use the response
                    if (regenerateResponse) {
                      newContent = regenerateResponse.content || regenerateResponse.response || JSON.stringify(regenerateResponse).substring(0, 500);
                      newData = regenerateResponse;
                      regenerated = true;
                    }
                  }
                } catch (error) {
                  console.error('Error regenerating marketing content:', error);
                  // Will be caught by outer catch block
                  throw error;
                }
                break;
                
              case 'pitch-deck':
                // Pitch Deck: Regenerate slides
                const pitchResponse = await pitchAPI.generateSlides(modificationContext);
                if (pitchResponse && pitchResponse.slides) {
                  newContent = `Generated ${pitchResponse.slides.length} slides: ${pitchResponse.slides.map(s => s.title).join(', ')}`;
                  newData = {
                    slides: pitchResponse.slides?.length || 0,
                    hasPowerPoint: !!pitchResponse.pptx_path,
                    hasGamma: !!pitchResponse.gamma_presentation?.success,
                  };
                  regenerated = true;
                }
                break;
                
              case 'patent':
              case 'patent-strategy':
                // Patent: Use assessPatentability or filingStrategy
                if (activityType === 'patent-strategy') {
                  const patentStrategyResponse = await patentAPI.filingStrategy(modificationContext);
                  if (patentStrategyResponse) {
                    newContent = patentStrategyResponse.strategy || patentStrategyResponse.response || patentStrategyResponse.content || JSON.stringify(patentStrategyResponse).substring(0, 500);
                    newData = patentStrategyResponse;
                    regenerated = true;
                  }
                } else {
                  const patentResponse = await patentAPI.assessPatentability(modificationContext);
                  if (patentResponse) {
                    newContent = patentResponse.assessment || patentResponse.response || patentResponse.content || JSON.stringify(patentResponse).substring(0, 500);
                    newData = patentResponse;
                    regenerated = true;
                  }
                }
                break;
                
              case 'policy':
              case 'privacy':
              case 'terms':
                // Policy: Determine which policy type and regenerate
                const isPrivacy = activityType === 'privacy' || (previousData?.policy_type && previousData.policy_type.includes('Privacy'));
                if (isPrivacy) {
                  const privacyResponse = await policyAPI.generatePrivacyPolicy(modificationContext);
                  if (privacyResponse) {
                    newContent = privacyResponse.policy || privacyResponse.content || privacyResponse.response || JSON.stringify(privacyResponse).substring(0, 500);
                    newData = privacyResponse;
                    regenerated = true;
                  }
                } else {
                  const termsResponse = await policyAPI.generateTermsOfService(modificationContext);
                  if (termsResponse) {
                    newContent = termsResponse.terms || termsResponse.content || termsResponse.response || JSON.stringify(termsResponse).substring(0, 500);
                    newData = termsResponse;
                    regenerated = true;
                  }
                }
                break;
                
              case 'team':
              case 'job-desc':
                // Team: Use analyzeTeamNeeds or generateJobDescription
                if (activityType === 'job-desc' && previousData?.role_title) {
                  const jobDescResponse = await teamAPI.generateJobDescription({
                    ...modificationContext,
                    role_title: previousData.role_title,
                    ...previousData
                  });
                  if (jobDescResponse) {
                    newContent = jobDescResponse.job_description || jobDescResponse.content || jobDescResponse.response || JSON.stringify(jobDescResponse).substring(0, 500);
                    newData = jobDescResponse;
                    regenerated = true;
                  }
                } else {
                  const teamResponse = await teamAPI.analyzeTeamNeeds(modificationContext);
                  if (teamResponse) {
                    newContent = teamResponse.analysis || teamResponse.recommendations || teamResponse.response || JSON.stringify(teamResponse).substring(0, 500);
                    newData = teamResponse;
                    regenerated = true;
                  }
                }
                break;
                
              case 'competitors':
                // Competitors: Regenerate analysis
                const competitorsResponse = await competitiveAPI.analyzeCompetitors(modificationContext);
                if (competitorsResponse) {
                  newContent = competitorsResponse.analysis || competitorsResponse.response || competitorsResponse.content || JSON.stringify(competitorsResponse).substring(0, 500);
                  newData = competitorsResponse;
                  regenerated = true;
                }
                break;
                
              case 'elevator':
                // Elevator Pitch: Regenerate
                const elevatorResponse = await pitchAPI.generateElevatorPitch(modificationContext);
                if (elevatorResponse) {
                  newContent = elevatorResponse.pitch || elevatorResponse.content || elevatorResponse.response || JSON.stringify(elevatorResponse).substring(0, 500);
                  newData = elevatorResponse;
                  regenerated = true;
                }
                break;
                
              default:
                // For other types, use chat response as content
                newContent = assistantResponse;
                regenerated = true;
                break;
            }
            
            // Update the activity with new content and keep previous version
            if (regenerated && newContent) {
              // Ensure previousContent is set (use current content if not already stored)
              const contentToSave = previousContent || latestActivityWithContent.content || '';
              
              console.log('🔄 Updating activity with new content:', {
                activityId: latestActivityWithContent.id,
                activityType: activityType,
                previousContentLength: contentToSave.length,
                newContentLength: newContent.length,
                hasNewData: !!newData
              });
              
              console.log('🔄 BEFORE UPDATE - Activity state:', {
                id: latestActivityWithContent.id,
                currentContent: latestActivityWithContent.content?.substring(0, 50),
                hasModified: latestActivityWithContent.modified,
                hasPreviousContent: !!latestActivityWithContent.previousContent
              });
              
              // Update activity with explicit state update to ensure re-render
              setActivities(prev => {
                const updated = prev.map(activity => 
                  activity.id === latestActivityWithContent.id ? { 
                    ...activity, 
                    modified: true, 
                    modification: userMessage,
                    modificationResponse: assistantResponse,
                    previousContent: contentToSave, // Keep previous version
                    previousData: previousData || latestActivityWithContent.data, // Keep previous data too
                    content: newContent, // Override with new content - THIS IS THE KEY
                    data: newData || previousData || latestActivityWithContent.data, // Update data with new results
                    isModification: true
                  } : activity
                );
                const modifiedActivity = updated.find(a => a.id === latestActivityWithContent.id);
                console.log('✅ AFTER UPDATE - Activity updated:', {
                  id: modifiedActivity.id,
                  modified: modifiedActivity.modified,
                  isModification: modifiedActivity.isModification,
                  hasPreviousContent: !!modifiedActivity.previousContent,
                  hasNewContent: !!modifiedActivity.content,
                  newContentPreview: modifiedActivity.content?.substring(0, 100),
                  previousContentPreview: modifiedActivity.previousContent?.substring(0, 100)
                });
                return updated;
              });
              
              // Update chat message to show regeneration success
              if (!chatError) {
                setChatMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: 'assistant',
                    content: `✅ I've updated the ${activityType.replace('-', ' ')} content based on your request. Check the Activity Report to see the changes. You can restore the previous version if needed.\n\n${assistantResponse}`
                  };
                  return updated;
                });
              }
            } else {
              // Regeneration failed or didn't happen - use chat response as new content
              console.warn('⚠️ Regeneration failed or returned no content. Using chat response as new content.', {
                regenerated,
                hasNewContent: !!newContent,
                activityType
              });
              
              // Still update the activity with chat response as new content
              const contentToSave = previousContent || latestActivityWithContent.content || '';
              
              console.log('🔄 Updating activity with chat response as new content:', {
                activityId: latestActivityWithContent.id,
                previousContentLength: contentToSave.length,
                newContentLength: assistantResponse.length
              });
              
              // Update activity with explicit state update
              setActivities(prev => {
                const updated = prev.map(activity => 
                  activity.id === latestActivityWithContent.id ? { 
                    ...activity, 
                    modified: true, 
                    modification: userMessage,
                    modificationResponse: assistantResponse,
                    previousContent: contentToSave, // Keep previous version
                    previousData: previousData || latestActivityWithContent.data, // Keep previous data
                    content: assistantResponse, // Use chat response as new content
                    isModification: true
                  } : activity
                );
                const modifiedActivity = updated.find(a => a.id === latestActivityWithContent.id);
                console.log('✅ Activity updated with chat response:', {
                  id: modifiedActivity.id,
                  modified: modifiedActivity.modified,
                  isModification: modifiedActivity.isModification,
                  hasPreviousContent: !!modifiedActivity.previousContent
                });
                return updated;
              });
            }
          } catch (error) {
            console.error(`Error regenerating ${activityType} content:`, error);
            // Even if regeneration fails, still overwrite with chat response
            const errorNote = `Modification requested but regeneration failed: ${error.message || 'Unknown error'}. Your request has been recorded.`;
            
            // Ensure previousContent is saved for version control
            const contentToSaveOnError = previousContent || latestActivityWithContent.content || '';
            
            updateActivity(latestActivityWithContent.id, { 
              modified: true, 
              modification: userMessage,
              modificationResponse: assistantResponse || errorNote,
              previousContent: contentToSaveOnError, // Save previous version for restore option
              previousData: previousData || latestActivityWithContent.data, // Save previous data
              content: assistantResponse || errorNote, // Overwrite with chat response, not original content
              isModification: true,
              regenerationFailed: true
            });
          }
        }
      }
      
      // Add chat activity ONLY if it's NOT a modification request (modifications update the original activity, not create a new chat entry)
      if (!chatError && !isModificationRequest) {
        addActivity('chat', 'Chat Message', { query: userMessage }, assistantResponse);
      }
      
      setLoading(prev => ({ ...prev, chat: false }));
    }
  };

  const handleGenerateSlides = () => {
    setLoading(prev => ({ ...prev, slides: true }));
    pitchAPI.generateSlides(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, slides: response }));
        addActivity('slides', 'Slides Generated', { slides: response.slides?.length || 0 });
      })
      .catch(error => {
        console.error('Error generating slides:', error);
        alert('Failed to generate slides. Please try again.');
      })
      .finally(() => setLoading(prev => ({ ...prev, slides: false })));
  };

  const handleGenerateElevatorPitch = () => {
    setLoading(prev => ({ ...prev, elevator: true }));
    pitchAPI.generateElevatorPitch(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, elevator: response }));
        const content = response.elevator_pitch || response.content || response.response || 'Elevator pitch generated';
        addActivity('elevator', 'Elevator Pitch Generated', response, content);
      })
      .catch(error => {
        console.error('Error generating elevator pitch:', error);
        alert('Failed to generate elevator pitch. Please try again.');
      })
      .finally(() => setLoading(prev => ({ ...prev, elevator: false })));
  };

  const handleAnalyzeCompetitors = () => {
    setLoading(prev => ({ ...prev, competitors: true }));
    competitiveAPI.analyzeCompetitors(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, competitors: response }));
        const content = response.analysis || response.summary || response.response || JSON.stringify(response).substring(0, 200);
        addActivity('competitors', 'Competitor Analysis', response, content);
      })
      .catch(error => {
        console.error('Error analyzing competitors:', error);
        alert('Failed to analyze competitors. Please try again.');
      })
      .finally(() => setLoading(prev => ({ ...prev, competitors: false })));
  };

  const handleDownloadPPT = (filename) => {
    pitchAPI.downloadPPT(filename)
      .then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
      })
      .catch(error => {
        console.error('Error downloading PPT:', error);
        alert('Failed to download PowerPoint file.');
      });
  };

  const handleGenerateInstagram = () => {
    setLoading(prev => ({ ...prev, instagram: true }));
    marketingAPI.generateInstagramContent(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, instagram: response }));
        addActivity('instagram', 'Instagram Content Generated', response);
      })
      .catch(error => {
        console.error('Error generating Instagram content:', error);
        alert('Failed to generate Instagram content.');
      })
      .finally(() => setLoading(prev => ({ ...prev, instagram: false })));
  };

  const handleGenerateLinkedIn = () => {
    setLoading(prev => ({ ...prev, linkedin: true }));
    marketingAPI.generateLinkedInContent(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, linkedin: response }));
        addActivity('linkedin', 'LinkedIn Content Generated', response);
      })
      .catch(error => {
        console.error('Error generating LinkedIn content:', error);
        alert('Failed to generate LinkedIn content.');
      })
      .finally(() => setLoading(prev => ({ ...prev, linkedin: false })));
  };

  const handleMarketingStrategies = () => {
    setLoading(prev => ({ ...prev, marketing: true }));
    marketingAPI.suggestMarketingStrategies(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, marketing: response }));
        addActivity('marketing', 'Marketing Strategies Generated', response);
      })
      .catch(error => {
        console.error('Error generating marketing strategies:', error);
        alert('Failed to generate marketing strategies.');
      })
      .finally(() => setLoading(prev => ({ ...prev, marketing: false })));
  };

  const handleGeneratePrivacyPolicy = () => {
    setLoading(prev => ({ ...prev, privacy: true }));
    policyAPI.generatePrivacyPolicy(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, privacy: response }));
        addActivity('privacy', 'Privacy Policy Generated', response);
      })
      .catch(error => {
        console.error('Error generating privacy policy:', error);
        alert('Failed to generate privacy policy.');
      })
      .finally(() => setLoading(prev => ({ ...prev, privacy: false })));
  };

  const handleGenerateTerms = () => {
    setLoading(prev => ({ ...prev, terms: true }));
    policyAPI.generateTermsOfService(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, terms: response }));
        addActivity('terms', 'Terms of Service Generated', response);
      })
      .catch(error => {
        console.error('Error generating terms of service:', error);
        alert('Failed to generate terms of service.');
      })
      .finally(() => setLoading(prev => ({ ...prev, terms: false })));
  };

  const handleOpenForm = async (type, title) => {
    setFormType(type);
    setFormTitle(title);
    setLoading(prev => ({ ...prev, [`form_${type}`]: true }));
    
    try {
      let questionnaire = [];
      switch (type) {
        case 'patent':
          questionnaire = await questionnaireAPI.getPatentQuestionnaire();
          break;
        case 'marketing':
          questionnaire = await questionnaireAPI.getMarketingQuestionnaire();
          break;
        case 'policy':
          questionnaire = await questionnaireAPI.getPolicyQuestionnaire();
          break;
        case 'team':
          questionnaire = await questionnaireAPI.getTeamQuestionnaire();
          break;
        default:
          break;
      }
      
      // Filter out company_name field - we'll use companyData instead
      questionnaire = questionnaire.filter(q => q.id !== 'company_name');
      
      setFormQuestionnaire(questionnaire);
      setShowForm(true);
    } catch (error) {
      console.error(`Error loading ${type} questionnaire:`, error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      console.error('Full error details:', error);
      alert(`Failed to load form: ${errorMsg}\n\nPlease check:\n1. Backend server is running (http://localhost:8000)\n2. Check browser console for details`);
    } finally {
      setLoading(prev => ({ ...prev, [`form_${type}`]: false }));
    }
  };

  const handleFormSubmit = (formData) => {
    // Get company name from companyData
    const companyName = companyData?.basic_info?.company_name || 
                       companyData?.companyName || 
                       companyData?.company_name || 
                       '';
    
    // Merge form data with company data, adding company_name if not present
    const mergedData = { 
      ...companyData, 
      ...formData,
      company_name: companyName // Always include company name from signup
    };
    
    setShowForm(false);
    
    // Call appropriate API based on form type
    switch (formType) {
      case 'patent':
        handleAssessPatentabilityWithData(mergedData);
        break;
      case 'marketing':
        handleMarketingWithData(mergedData);
        break;
      case 'policy':
        handlePolicyWithData(mergedData);
        break;
      case 'team':
        handleTeamWithData(mergedData);
        break;
      case 'job-description':
        handleJobDescriptionWithData(mergedData);
        break;
      default:
        break;
    }
  };

  const handleAssessPatentabilityWithData = (data) => {
    setLoading(prev => ({ ...prev, patent: true }));
    patentAPI.assessPatentability(data)
      .then(response => {
        setResults(prev => ({ ...prev, patent: response }));
        const content =
          response.assessment ||
          response.summary ||
          response.response ||
          response.content ||
          JSON.stringify(response).substring(0, 400);
        addActivity('patent', 'Patentability Assessed', response, content);
      })
      .catch(error => {
        console.error('Error assessing patentability:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to assess patentability.';
        alert(errorMsg);
      })
      .finally(() => setLoading(prev => ({ ...prev, patent: false })));
  };

  const handleGenerateMarketingFromPrompt = () => {
    if (!marketingPrompt.trim()) {
      alert('Please enter a prompt describing what you want to generate');
      return;
    }
    
    setLoading(prev => ({ ...prev, marketing: true }));
    
    marketingAPI.generateFromPrompt(marketingPrompt, companyData)
      .then(response => {
        if (response.success && response.results) {
          const results = response.results;
          
          // Extract image URLs from results
          const imageUrls = [];
          const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          
          results.forEach(r => {
            console.log(`Checking ${r.platform} for image:`, r.data); // Debug log
            
            // Check multiple possible locations for image URL
            let imageUrl = r.data.image_url || r.data.imageUrl || (r.data.response && r.data.response.image_url);
            const imageGenerated = r.data.image_generated;
            
            // If it's a relative URL (starts with /), construct full URL
            if (imageUrl && imageUrl.startsWith('/')) {
              imageUrl = `${API_BASE_URL}${imageUrl}`;
            }
            
            console.log(`${r.platform} - image_url:`, imageUrl, 'image_generated:', imageGenerated); // Debug log
            
            if (imageUrl) {
              imageUrls.push({
                platform: r.platform,
                url: imageUrl,
                prompt: r.data.image_prompt || r.data.prompt_used || r.data.image_prompt_description
              });
            } else if (imageGenerated === false) {
              console.warn(`${r.platform} - Image generation failed or was not attempted`);
            }
          });
          
          // Store results with imageUrls for display
          const activityData = {
            results: results,
            imageUrls: imageUrls
          };
          
          const allContent = results.map(r => {
            const content = r.data.content || r.data.posts || r.data.strategies || r.data.response || JSON.stringify(r.data).substring(0, 200);
            return `**${r.platform}:**\n${content}`;
          }).join('\n\n');
          
          console.log('Final marketing results with images:', { results, imageUrls, activityData }); // Debug log
          
          setResults(prev => ({ ...prev, marketing: results }));
          addActivity('marketing', `Marketing Content Generated: ${marketingPrompt}`, activityData, allContent);
          
          // Reset prompt
          setMarketingPrompt('');
          setShowMarketingPrompt(false);
        } else {
          alert(response.message || 'Failed to generate marketing content');
        }
      })
      .catch(error => {
        console.error('Error generating marketing from prompt:', error);
        alert('Failed to generate marketing content. Please try again.');
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, marketing: false }));
      });
  };

  const handleMarketingWithData = (data) => {
    setLoading(prev => ({ ...prev, marketing: true }));
    
    // Check which platform(s) user selected
    const platforms = data.platform || [];
    const hasInstagram = platforms.includes('Instagram') || platforms.includes('Both');
    const hasLinkedIn = platforms.includes('LinkedIn') || platforms.includes('Both');
    
    // Generate content based on platform selection
    const promises = [];
    
    if (hasInstagram) {
      promises.push(marketingAPI.generateInstagramContent(data).then(r => ({ platform: 'Instagram', data: r })));
    }
    
    if (hasLinkedIn) {
      promises.push(marketingAPI.generateLinkedInContent(data).then(r => ({ platform: 'LinkedIn', data: r })));
    }
    
    // If no specific platform or both, also generate strategies
    if (promises.length === 0 || platforms.includes('Both')) {
      promises.push(marketingAPI.suggestMarketingStrategies(data).then(r => ({ platform: 'Strategies', data: r })));
    }
    
    Promise.all(promises)
      .then(results => {
        const allContent = results.map(r => {
          const content = r.data.content || r.data.posts || r.data.strategies || r.data.response || JSON.stringify(r.data).substring(0, 200);
          return `**${r.platform}:**\n${content}`;
        }).join('\n\n');
        
        // Extract image URLs from results
        const imageUrls = [];
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        
        results.forEach(r => {
          console.log(`Checking ${r.platform} for image:`, r.data); // Debug log
          
          // Check multiple possible locations for image URL
          let imageUrl = r.data.image_url || r.data.imageUrl || (r.data.response && r.data.response.image_url);
          const imageGenerated = r.data.image_generated;
          
          // If it's a relative URL (starts with /), construct full URL
          if (imageUrl && imageUrl.startsWith('/')) {
            imageUrl = `${API_BASE_URL}${imageUrl}`;
          }
          
          console.log(`${r.platform} - image_url:`, imageUrl, 'image_generated:', imageGenerated); // Debug log
          
          if (imageUrl) {
            imageUrls.push({
              platform: r.platform,
              url: imageUrl,
              prompt: r.data.image_prompt || r.data.prompt_used || r.data.image_prompt_description
            });
          } else if (imageGenerated === false) {
            console.warn(`${r.platform} - Image generation failed or was not attempted`);
          }
        });
        
        // Store results with imageUrls for display
        const activityData = {
          results: results,
          imageUrls: imageUrls
        };
        
        console.log('Final marketing results with images:', { results, imageUrls, activityData }); // Debug log
        
        setResults(prev => ({ ...prev, marketing: results }));
        addActivity('marketing', 'Marketing Content Generated', activityData, allContent);
      })
      .catch(error => {
        console.error('Error generating marketing content:', error);
        alert('Failed to generate marketing content.');
      })
      .finally(() => setLoading(prev => ({ ...prev, marketing: false })));
  };

  const handleGeneratePolicyFromPrompt = () => {
    if (!policyPrompt.trim()) {
      alert('Please enter a prompt describing what policy you need');
      return;
    }
    
    setLoading(prev => ({ ...prev, policy: true }));
    
    // Determine policy type from prompt
    const promptLower = policyPrompt.toLowerCase();
    const isPrivacy = promptLower.includes('privacy') || promptLower.includes('data protection') || promptLower.includes('gdpr');
    const isTerms = promptLower.includes('terms') || promptLower.includes('tos') || promptLower.includes('terms of service');
    
    // Merge prompt with company data
    const policyContext = {
      ...companyData,
      user_prompt: policyPrompt,
      policy_type: isPrivacy ? 'Privacy Policy' : (isTerms ? 'Terms of Service' : 'Privacy Policy') // Default to Privacy
    };
    
    if (isPrivacy || (!isTerms && !isPrivacy)) {
      // Generate Privacy Policy
      policyAPI.generatePrivacyPolicy(policyContext)
        .then(response => {
          const content = response.policy || response.content || response.response || JSON.stringify(response).substring(0, 500);
          addActivity('privacy', `Privacy Policy: ${policyPrompt}`, response, content);
          setPolicyPrompt('');
          setShowPolicyPrompt(false);
        })
        .catch(error => {
          console.error('Error generating privacy policy from prompt:', error);
          const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate privacy policy.';
          alert(errorMsg);
        })
        .finally(() => setLoading(prev => ({ ...prev, policy: false })));
    } else {
      // Generate Terms of Service
      policyAPI.generateTermsOfService(policyContext)
        .then(response => {
          const content = response.terms || response.content || response.response || JSON.stringify(response).substring(0, 500);
          addActivity('terms', `Terms of Service: ${policyPrompt}`, response, content);
          setPolicyPrompt('');
          setShowPolicyPrompt(false);
        })
        .catch(error => {
          console.error('Error generating terms of service from prompt:', error);
          const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate terms of service.';
          alert(errorMsg);
        })
        .finally(() => setLoading(prev => ({ ...prev, policy: false })));
    }
  };

  const handleGenerateTeamFromPrompt = () => {
    if (!teamPrompt.trim()) {
      alert('Please enter a prompt describing your team needs');
      return;
    }
    
    setLoading(prev => ({ ...prev, team: true }));
    
    // Merge prompt with company data
    const teamContext = {
      ...companyData,
      user_prompt: teamPrompt
    };
    
    // Use query endpoint which can handle prompts intelligently
    teamAPI.queryTeam(teamPrompt, teamContext)
      .then(response => {
        const content = response.analysis || response.recommendations || response.response || response.content || JSON.stringify(response).substring(0, 500);
        addActivity('team', `Team Analysis: ${teamPrompt}`, response, content);
        setTeamPrompt('');
        setShowTeamPrompt(false);
      })
      .catch(error => {
        console.error('Error generating team analysis from prompt:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate team analysis.';
        alert(errorMsg);
      })
      .finally(() => setLoading(prev => ({ ...prev, team: false })));
  };

  const handleAssessPatentability = () => {
    setShowPatentPrompt(true);
  };

  const handleGeneratePatentFromPrompt = () => {
    if (!patentPrompt.trim()) {
      alert('Please enter a prompt describing your patent needs');
      return;
    }
    
    setLoading(prev => ({ ...prev, patent: true }));
    
    // Use query endpoint which can handle prompts intelligently
    patentAPI.queryPatent(patentPrompt, companyData)
      .then(response => {
        const content = response.assessment || response.response || response.content || JSON.stringify(response).substring(0, 500);
        addActivity('patent', `Patent Assessment: ${patentPrompt}`, response, content);
        setPatentPrompt('');
        setShowPatentPrompt(false);
      })
      .catch(error => {
        console.error('Error generating patent assessment from prompt:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate patent assessment.';
        alert(errorMsg);
      })
      .finally(() => setLoading(prev => ({ ...prev, patent: false })));
  };

  const handleFilingStrategy = () => {
    setLoading(prev => ({ ...prev, patentStrategy: true }));
    patentAPI.filingStrategy(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, patentStrategy: response }));
        addActivity('patent-strategy', 'Filing Strategy Generated', response);
      })
      .catch(error => {
        console.error('Error generating filing strategy:', error);
        alert('Failed to generate filing strategy.');
      })
      .finally(() => setLoading(prev => ({ ...prev, patentStrategy: false })));
  };

  const handleAnalyzeTeamNeeds = () => {
    setLoading(prev => ({ ...prev, team: true }));
    teamAPI.analyzeTeamNeeds(companyData)
      .then(response => {
        setResults(prev => ({ ...prev, team: response }));
        addActivity('team', 'Team Needs Analyzed', response);
      })
      .catch(error => {
        console.error('Error analyzing team needs:', error);
        alert('Failed to analyze team needs.');
      })
      .finally(() => setLoading(prev => ({ ...prev, team: false })));
  };

  const handleOpenJobDescriptionForm = async () => {
    setShowJobDescPrompt(true);
  };

  const handleGenerateJobDescriptionFromPrompt = () => {
    if (!jobDescPrompt.trim()) {
      alert('Please enter a prompt describing the job role you want to hire for');
      return;
    }
    
    setLoading(prev => ({ ...prev, jobDesc: true }));
    
    // Extract role title from prompt (simple extraction - first few words or explicit mention)
    const promptLower = jobDescPrompt.toLowerCase();
    let roleTitle = '';
    
    // Try to extract role title from common patterns
    if (promptLower.includes('role:') || promptLower.includes('position:')) {
      const match = jobDescPrompt.match(/(?:role|position):\s*([^,\n]+)/i);
      if (match) roleTitle = match[1].trim();
    } else if (promptLower.includes('hire') || promptLower.includes('looking for')) {
      // Extract after "hire" or "looking for"
      const match = jobDescPrompt.match(/(?:hire|looking for|need)\s+(?:a|an)?\s*([^,\n]+)/i);
      if (match) roleTitle = match[1].trim();
    } else {
      // Use first few words as role title
      roleTitle = jobDescPrompt.split(/[,\n]/)[0].trim().substring(0, 50);
    }
    
    if (!roleTitle) {
      roleTitle = 'New Role'; // Default fallback
    }
    
    // Build payload with prompt as additional context
    const payload = {
      role_title: roleTitle,
      role_details: {
        additional_requirements: jobDescPrompt,
        user_prompt: jobDescPrompt
      },
      company_context: companyData,
      team_context: companyData,
    };
    
    teamAPI.generateJobDescription(payload)
      .then(response => {
        let content = response.job_description || response.description || response.response || JSON.stringify(response).substring(0, 500);
        // Strip markdown from job description content
        if (content) {
          content = stripMarkdown(content);
        }
        addActivity('job-desc', `Job Description: ${roleTitle}`, response, content);
        setJobDescPrompt('');
        setShowJobDescPrompt(false);
      })
      .catch(error => {
        console.error('Error generating job description from prompt:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate job description.';
        alert(errorMsg);
      })
      .finally(() => setLoading(prev => ({ ...prev, jobDesc: false })));
  };

  const handleJobDescriptionWithData = (data) => {
    setLoading(prev => ({ ...prev, jobDesc: true }));
    
    // Structure the data as expected by the backend
    const payload = {
      role_title: data.role_title,
      role_details: {
        experience_level: data.experience_level,
        must_have_skills: data.must_have_skills,
        nice_to_have_skills: data.nice_to_have_skills,
        employment_type: data.employment_type,
        equity_offering: data.equity_offering,
        start_date: data.start_date,
        additional_requirements: data.additional_requirements,
      },
      company_context: companyData,
      team_context: companyData,
    };
    
    teamAPI.generateJobDescription(payload)
      .then(response => {
        setResults(prev => ({ ...prev, jobDesc: response }));
        let content = response.job_description || response.description || response.response || JSON.stringify(response).substring(0, 300);
        // Strip markdown from job description content
        if (content) {
          content = stripMarkdown(content);
        }
        addActivity('job-desc', 'Job Description Generated', response, content);
      })
      .catch(error => {
        console.error('Error generating job description:', error);
        const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate job description.';
        alert(errorMsg);
      })
      .finally(() => setLoading(prev => ({ ...prev, jobDesc: false })));
  };

  const pitchDeckResult = results.pitchDeck;
  const companyName = companyData?.basic_info?.company_name || companyData?.companyName || 'Your Company';

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-violet-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-purple-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-violet-600 bg-clip-text text-transparent">
            Welcome back, {companyName}! 👋
          </h1>
          <p className="text-gray-600 mt-2">Your AI-powered startup toolkit is ready.</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-7 space-y-8">
            {/* Pitch Deck Result - Comparison View */}
            {pitchDeckResult && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-800">Your Pitch Deck - Compare Options</h2>
                  <span className="text-sm text-gray-500">Choose your preferred format</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* PowerPoint Option */}
                  {pitchDeckResult.pptx_path && (
                    <div className="border-2 border-purple-200 rounded-lg p-4 hover:border-purple-400 transition-colors">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold">PPT</span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-800">PowerPoint Deck</h3>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">
                        Traditional PowerPoint presentation with {pitchDeckResult.total_slides || pitchDeckResult.slides?.length || 0} slides
                      </p>
                      <button
                        onClick={() => setShowPPTPreview(true)}
                        className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all font-medium"
                      >
                        Preview PowerPoint
                      </button>
                    </div>
                  )}

                  {/* Gamma Option */}
                  {pitchDeckResult.gamma_presentation?.success ? (
                    <div className="border-2 border-purple-200 rounded-lg p-4 hover:border-purple-400 transition-colors">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-violet-600 rounded-lg flex items-center justify-center">
                          <span className="text-white font-bold">γ</span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-800">Gamma Presentation</h3>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">
                        AI-enhanced interactive presentation with modern design
                      </p>
                      <a
                        href={pitchDeckResult.gamma_presentation.presentation_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full bg-gradient-to-r from-purple-500 to-violet-600 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-violet-700 transition-all font-medium text-center"
                      >
                        Open Gamma Presentation
                      </a>
                    </div>
                  ) : pitchDeckResult.gamma_presentation ? (
                    <div className="border-2 border-red-200 rounded-lg p-4 bg-red-50">
                      <p className="text-sm text-red-600">
                        Gamma generation failed: {pitchDeckResult.gamma_presentation.message || pitchDeckResult.gamma_presentation.error}
                      </p>
                    </div>
                  ) : null}

                  {!pitchDeckResult.pptx_path && !pitchDeckResult.gamma_presentation && (
                    <div className="col-span-2 text-center py-8 text-gray-500">
                      <p>Generating presentations... Please wait.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Pitch & Presentation Section */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="h-1 w-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded"></div>
                <h2 className="text-2xl font-bold text-gray-800">Pitch & Presentation</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={handleGeneratePitchDeck}
                  disabled={loading.pitchDeck}
                  className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl">✨</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Generate Pitch Deck</h3>
                  <p className="text-sm text-gray-600">
                    Create a complete pitch deck (PowerPoint + Gamma).
                  </p>
                  {loading.pitchDeck && (
                    <div className="mt-4 text-purple-600 text-sm">Generating... (This may take 1-2 minutes)</div>
                  )}
                </button>

                <button
                  onClick={handleGenerateElevatorPitch}
                  disabled={loading.elevator}
                  className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-red-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl">🎤</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Elevator Pitch</h3>
                  <p className="text-sm text-gray-600">
                    Generate a 60-second elevator pitch.
                  </p>
                  {loading.elevator && (
                    <div className="mt-4 text-purple-600 text-sm">Generating...</div>
                  )}
                </button>
              </div>
            </div>

            {/* Market Intelligence Section */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="h-1 w-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded"></div>
                <h2 className="text-2xl font-bold text-gray-800">Market Intelligence</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={handleAnalyzeCompetitors}
                  disabled={loading.competitors}
                  className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Analyze Competitors</h3>
                  <p className="text-sm text-gray-600">
                    Get competitive intelligence and market insights.
                  </p>
                  {loading.competitors && (
                    <div className="mt-4 text-purple-600 text-sm">Analyzing...</div>
                  )}
                </button>

                {!showMarketingPrompt ? (
                  <button
                    onClick={() => setShowMarketingPrompt(true)}
                    disabled={loading.marketing}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl">📢</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Marketing Strategies</h3>
                    <p className="text-sm text-gray-600">
                      Generate content from your prompt.
                    </p>
                    {loading.marketing && (
                      <div className="mt-4 text-purple-600 text-sm">Generating...</div>
                    )}
                  </button>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-md border border-purple-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">📢 Generate Marketing Content</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Describe what you want to generate. For example: "Generate an Instagram post with image for my product" or "Create LinkedIn content with trendy style and image"
                    </p>
                    <textarea
                      value={marketingPrompt}
                      onChange={(e) => setMarketingPrompt(e.target.value)}
                      placeholder="e.g., Generate an Instagram post with image for DataViz Pro, trendy style, targeting startup founders"
                      className="w-full p-3 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4 min-h-[100px]"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleGenerateMarketingFromPrompt}
                        disabled={loading.marketing || !marketingPrompt.trim()}
                        className="flex-1 bg-gradient-to-r from-purple-500 to-violet-600 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-violet-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading.marketing ? 'Generating...' : 'Generate'}
                      </button>
                      <button
                        onClick={() => {
                          setShowMarketingPrompt(false);
                          setMarketingPrompt('');
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {!showPolicyPrompt ? (
                  <button
                    onClick={() => setShowPolicyPrompt(true)}
                    disabled={loading.policy}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl">🔒</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Policy & Compliance</h3>
                    <p className="text-sm text-gray-600">
                      Generate privacy policy or terms of service from your prompt.
                    </p>
                    {loading.policy && (
                      <div className="mt-4 text-purple-600 text-sm">Generating...</div>
                    )}
                  </button>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-md border border-purple-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">🔒 Generate Policy</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Describe what policy you need. Mention "privacy policy" or "terms of service" in your prompt. For example: "Generate a privacy policy for my SaaS startup" or "Create terms of service for my mobile app"
                    </p>
                    <textarea
                      value={policyPrompt}
                      onChange={(e) => setPolicyPrompt(e.target.value)}
                      placeholder="e.g., Generate a comprehensive privacy policy for my data analytics startup that handles user data..."
                      className="w-full p-3 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4 min-h-[100px]"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleGeneratePolicyFromPrompt}
                        disabled={loading.policy || !policyPrompt.trim()}
                        className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading.policy ? 'Generating...' : 'Generate Policy'}
                      </button>
                      <button
                        onClick={() => {
                          setShowPolicyPrompt(false);
                          setPolicyPrompt('');
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Patent & IP Section */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="h-1 w-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded"></div>
                <h2 className="text-2xl font-bold text-gray-800">Patent & IP</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {!showPatentPrompt ? (
                  <button
                    onClick={() => setShowPatentPrompt(true)}
                    disabled={loading.patent}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl">⚖️</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Assess Patentability</h3>
                    <p className="text-sm text-gray-600">Describe your invention to assess patentability.</p>
                    {loading.patent && (
                      <div className="mt-4 text-purple-600 text-sm">Analyzing...</div>
                    )}
                  </button>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-md border border-purple-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">⚖️ Assess Patentability</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Describe your invention, technology, or idea. For example: "I have an AI-powered analytics platform that uses machine learning to predict market trends"
                    </p>
                    <textarea
                      value={patentPrompt}
                      onChange={(e) => setPatentPrompt(e.target.value)}
                      placeholder="e.g., Describe your invention, its unique features, and what problem it solves..."
                      className="w-full p-3 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4 min-h-[100px]"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleGeneratePatentFromPrompt}
                        disabled={loading.patent || !patentPrompt.trim()}
                        className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading.patent ? 'Analyzing...' : 'Assess Patentability'}
                      </button>
                      <button
                        onClick={() => {
                          setShowPatentPrompt(false);
                          setPatentPrompt('');
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleFilingStrategy}
                  disabled={loading.patentStrategy}
                  className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl">📝</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Filing Strategy</h3>
                  <p className="text-sm text-gray-600">Get patent filing strategy.</p>
                </button>
              </div>
            </div>

            {/* Team Section */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="h-1 w-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded"></div>
                <h2 className="text-2xl font-bold text-gray-800">Team</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {!showTeamPrompt ? (
                  <button
                    onClick={() => setShowTeamPrompt(true)}
                    disabled={loading.team}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl">👥</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Team Analysis</h3>
                    <p className="text-sm text-gray-600">Describe your team needs and get recommendations</p>
                    {loading.team && (
                      <div className="mt-4 text-purple-600 text-sm">Analyzing...</div>
                    )}
                  </button>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-md border border-purple-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">👥 Team Analysis</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Describe your team needs, hiring goals, or organizational challenges.
                    </p>
                    <textarea
                      value={teamPrompt}
                      onChange={(e) => setTeamPrompt(e.target.value)}
                      placeholder="e.g., I'm building a tech startup and need recommendations on what roles to hire first..."
                      className="w-full p-3 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4 min-h-[100px]"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleGenerateTeamFromPrompt}
                        disabled={loading.team || !teamPrompt.trim()}
                        className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-cyan-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading.team ? 'Analyzing...' : 'Analyze'}
                      </button>
                      <button
                        onClick={() => {
                          setShowTeamPrompt(false);
                          setTeamPrompt('');
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {!showJobDescPrompt ? (
                  <button
                    onClick={() => setShowJobDescPrompt(true)}
                    disabled={loading.jobDesc}
                    className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all border border-purple-100 hover:border-purple-300 group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl">💼</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Job Description</h3>
                    <p className="text-sm text-gray-600">Describe the role you want to hire for</p>
                    {loading.jobDesc && (
                      <div className="mt-4 text-purple-600 text-sm">Generating...</div>
                    )}
                  </button>
                ) : (
                  <div className="bg-white rounded-xl p-6 shadow-md border border-purple-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">💼 Generate Job Description</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Describe the role you want to hire for. Include the job title and key requirements. For example: "I need to hire a Senior Software Engineer with 5+ years experience in Python and React"
                    </p>
                    <textarea
                      value={jobDescPrompt}
                      onChange={(e) => setJobDescPrompt(e.target.value)}
                      placeholder="e.g., I need to hire a Senior Full Stack Developer with experience in React, Node.js, and AWS. Must have startup experience..."
                      className="w-full p-3 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-4 min-h-[100px]"
                    />
                    <div className="flex gap-3">
                      <button
                        onClick={handleGenerateJobDescriptionFromPrompt}
                        disabled={loading.jobDesc || !jobDescPrompt.trim()}
                        className="flex-1 bg-gradient-to-r from-purple-500 to-pink-600 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading.jobDesc ? 'Generating...' : 'Generate JD'}
                      </button>
                      <button
                        onClick={() => {
                          setShowJobDescPrompt(false);
                          setJobDescPrompt('');
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Activity Report Sidebar */}
          <div className="lg:col-span-5">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-200 sticky top-8 h-[calc(100vh-140px)] flex flex-col">
              <div className="mb-4 pb-3 border-b border-purple-100">
                <h2 className="text-xl font-bold text-gray-800 mb-1">Activity Report</h2>
                <p className="text-sm text-gray-600">Track your selections</p>
              </div>
              <div className="space-y-3 flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {activities.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-violet-100 rounded-full flex items-center justify-center mx-auto mb-4 shadow-inner">
                      <span className="text-3xl">📄</span>
                    </div>
                    <p className="text-base font-medium text-gray-500">No activities yet</p>
                    <p className="text-sm mt-2 text-gray-400">Your selections and generated content will appear here</p>
                  </div>
                ) : (
                  activities.map((activity) => (
                    <div
                      key={activity.id}
                      className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg p-3 border border-purple-200 shadow-sm hover:shadow transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-semibold text-gray-800">{activity.title}</p>
                            {activity.modified && (
                              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Modified</span>
                            )}
                            {activity.status === 'approved' && (
                              <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">Liked</span>
                            )}
                            {activity.status === 'needs_changes' && (
                              <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded">Needs change</span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                          
                          {/* Display Images if available */}
                          {(() => {
                            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                            
                            // Check for images in multiple possible locations
                            let imageUrls = activity.data?.imageUrls || 
                                            (activity.data?.results && activity.data.results.flatMap(r => {
                                              // Check multiple possible image URL locations
                                              const imageUrl = r.data?.image_url || 
                                                              r.data?.imageUrl || 
                                                              (r.data?.response && r.data.response.image_url) ||
                                                              r.image_url;
                                              
                                              if (imageUrl) {
                                                return [{
                                                  platform: r.platform || 'Marketing',
                                                  url: imageUrl,
                                                  prompt: r.data?.image_prompt || r.data?.prompt_used || r.data?.image_prompt_description
                                                }];
                                              }
                                              return [];
                                            }));
                            
                            // Convert relative URLs to full URLs and ensure proper format
                            if (imageUrls && Array.isArray(imageUrls)) {
                              imageUrls = imageUrls.map(img => {
                                let url = img.url;
                                // If it's a relative URL (starts with /), construct full URL
                                if (url && url.startsWith('/')) {
                                  url = `${API_BASE_URL}${url}`;
                                }
                                // Ensure URL is valid
                                if (url && !url.startsWith('http')) {
                                  url = `${API_BASE_URL}${url.startsWith('/') ? url : '/' + url}`;
                                }
                                return {
                                  ...img,
                                  url: url
                                };
                              }).filter(img => img.url); // Remove any invalid URLs
                            }
                            
                            console.log('Image URLs for display:', imageUrls); // Debug log
                            
                            if (imageUrls && Array.isArray(imageUrls) && imageUrls.length > 0) {
                              return (
                                <div className="mt-2 space-y-2">
                                  {imageUrls.map((img, idx) => (
                                    <div key={idx} className="bg-white rounded border border-purple-200 p-2">
                                      <p className="text-xs font-semibold text-gray-700 mb-1">{img.platform} Image:</p>
                                  <div className="relative w-full flex justify-center bg-gray-50 rounded" style={{ maxHeight: '300px', overflow: 'hidden', minHeight: '200px' }}>
                                    {img.url ? (
                                      <>
                                        <img
                                          src={img.url}
                                          alt={`${img.platform} marketing image`}
                                          className="rounded object-contain"
                                          style={{ maxHeight: '300px', maxWidth: '100%', height: 'auto' }}
                                          onError={(e) => {
                                            console.error('Image load error:', img.url, e);
                                            e.target.style.display = 'none';
                                            const errorDiv = e.target.nextElementSibling;
                                            if (errorDiv) errorDiv.style.display = 'block';
                                          }}
                                          onLoad={() => {
                                            console.log('Image loaded successfully:', img.url);
                                          }}
                                        />
                                        <div style={{ display: 'none' }} className="text-xs text-gray-500 p-2 text-center">
                                          <p>Image failed to load.</p>
                                          <p className="text-xs text-gray-400 break-all">{img.url}</p>
                                          <a href={img.url} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline mt-2 inline-block">
                                            Open in new tab →
                                          </a>
                                        </div>
                                      </>
                                    ) : (
                                      <div className="text-xs text-gray-500 p-4 text-center">
                                        <p>Image URL not available</p>
                                        <p className="text-xs text-gray-400 mt-1">Image may have expired or failed to generate</p>
                                      </div>
                                    )}
                                  </div>
                                      <a
                                        href={img.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-purple-600 hover:underline mt-1 inline-block"
                                      >
                                        Open full image →
                                      </a>
                                    </div>
                                  ))}
                                </div>
                              );
                            }
                            return null;
                          })()}
                          
                          {activity.content && (
                            <div className="mt-2 p-2 bg-white rounded border border-purple-200">
                              <div className="text-xs text-gray-700 prose prose-sm max-w-none">
                                {activity.type === 'job-desc' ? (
                                  // Job Description: Display as plain text (no markdown)
                                  <div className="whitespace-pre-wrap">
                                    {expandedActivityId === activity.id ? activity.content : `${activity.content.substring(0, 220)}${activity.content.length > 220 ? '…' : ''}`}
                                  </div>
                                ) : (
                                  // Other activities: Display with markdown rendering
                                  expandedActivityId === activity.id ? (
                                    <ReactMarkdown
                                      components={{
                                        h1: ({node, ...props}) => <h1 className="text-sm font-bold mb-2" {...props} />,
                                        h2: ({node, ...props}) => <h2 className="text-sm font-bold mb-2" {...props} />,
                                        h3: ({node, ...props}) => <h3 className="text-xs font-bold mb-1" {...props} />,
                                        h4: ({node, ...props}) => <h4 className="text-xs font-semibold mb-1" {...props} />,
                                        p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                                        ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                                        ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                                        li: ({node, ...props}) => <li className="ml-2" {...props} />,
                                        strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                                        em: ({node, ...props}) => <em className="italic" {...props} />,
                                        code: ({node, ...props}) => <code className="bg-gray-100 px-1 rounded text-xs" {...props} />,
                                      }}
                                    >
                                      {activity.content}
                                    </ReactMarkdown>
                                  ) : (
                                    <ReactMarkdown
                                      components={{
                                        p: ({node, ...props}) => <p className="mb-1" {...props} />,
                                      }}
                                    >
                                      {`${activity.content.substring(0, 220)}${activity.content.length > 220 ? '…' : ''}`}
                                    </ReactMarkdown>
                                  )
                                )}
                              </div>
                              {activity.content.length > 220 && (
                                <button
                                  onClick={() => setExpandedActivityId(expandedActivityId === activity.id ? null : activity.id)}
                                  className="mt-1 text-xs text-purple-600 hover:underline"
                                >
                                  {expandedActivityId === activity.id ? 'Show less' : 'Show more'}
                                </button>
                              )}
                            </div>
                          )}
                          {(activity.isModification || activity.modified) && activity.previousContent && (
                            <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                              {activity.regenerationFailed ? (
                                <p className="text-xs font-semibold text-orange-800 mb-2">⚠️ Modification requested but regeneration failed. Your request has been recorded. The original content is still shown.</p>
                              ) : (
                                <p className="text-xs font-semibold text-blue-800 mb-2">⚠️ This content was modified. Choose which version you want to keep.</p>
                              )}
                              <div className="flex gap-2">
                                <button
                                  onClick={() => {
                                    // Restore previous content and data, remove all modification flags
                                    updateActivity(activity.id, {
                                      content: activity.previousContent,
                                      data: activity.previousData || activity.data, // Restore previous data if available
                                      isModification: false,
                                      modified: false,
                                      previousContent: null,
                                      previousData: null,
                                      modification: null,
                                      modificationResponse: null,
                                      regenerationFailed: false
                                    });
                                  }}
                                  className="text-xs px-3 py-1 rounded bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors font-medium"
                                >
                                  ↶ Restore Previous Version
                                </button>
                                <button
                                  onClick={() => {
                                    // Keep current version, completely remove previous version and all modification flags
                                    updateActivity(activity.id, {
                                      previousContent: null,
                                      previousData: null,
                                      isModification: false,
                                      modified: false,
                                      modification: null,
                                      modificationResponse: null,
                                      regenerationFailed: false
                                    });
                                  }}
                                  className="text-xs px-3 py-1 rounded bg-green-100 text-green-800 hover:bg-green-200 transition-colors font-medium"
                                >
                                  ✓ Keep Current Version
                                </button>
                              </div>
                            </div>
                          )}
                          {activity.modification && !activity.isModification && (
                            <div className="mt-2 p-2 bg-yellow-50 rounded border border-yellow-200">
                              <p className="text-xs font-semibold text-yellow-800">Request: {activity.modification}</p>
                              {activity.modificationResponse && (
                                <div className="text-xs text-yellow-700 mt-1 prose prose-sm max-w-none">
                                  <ReactMarkdown
                                    components={{
                                      p: ({node, ...props}) => <p className="mb-1" {...props} />,
                                    }}
                                  >
                                    {activity.modificationResponse.substring(0, 200)}...
                                  </ReactMarkdown>
                                </div>
                              )}
                            </div>
                          )}
                          <div className="flex gap-2 mt-3">
                            <button
                              onClick={() => handleActivityStatus(activity.id, 'approved')}
                              className="text-xs px-3 py-1.5 rounded-lg bg-green-100 text-green-800 hover:bg-green-200 font-medium transition-colors shadow-sm"
                            >
                              👍 Looks good
                            </button>
                            <button
                              onClick={() => {
                                handleActivityStatus(activity.id, 'needs_changes');
                                setShowChat(true);
                              }}
                              className="text-xs px-3 py-1.5 rounded-lg bg-red-100 text-red-800 hover:bg-red-200 font-medium transition-colors shadow-sm"
                            >
                              ✏️ Ask changes
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
              
              {/* Download Report Button */}
              {activities.length > 0 && (
                <div className="mt-4 pt-4 border-t border-purple-200 flex-shrink-0">
                  <button
                    onClick={handleDownloadReport}
                    className="w-full bg-gradient-to-r from-purple-500 to-violet-600 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-violet-700 transition-all font-medium flex items-center justify-center gap-2"
                  >
                    <span>📥</span>
                    <span>Download Full Report</span>
                  </button>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    Download all activities and generated content
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Task Bar */}
      {showChat && (
        <div className="fixed bottom-0 right-0 w-96 h-[500px] bg-white rounded-t-xl shadow-2xl border border-purple-200 z-50 flex flex-col">
          <div className="bg-gradient-to-r from-purple-500 to-violet-600 text-white p-4 rounded-t-xl flex items-center justify-between">
            <h3 className="font-semibold">AI Assistant</h3>
            <button
              onClick={() => setShowChat(false)}
              className="text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-sm">Ask me anything about pitch decks, marketing, patents, and more!</p>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <div className="text-sm prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          h1: ({node, ...props}) => <h1 className="text-sm font-bold mb-2" {...props} />,
                          h2: ({node, ...props}) => <h2 className="text-sm font-bold mb-2" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-xs font-bold mb-1" {...props} />,
                          h4: ({node, ...props}) => <h4 className="text-xs font-semibold mb-1" {...props} />,
                          p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                          ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                          li: ({node, ...props}) => <li className="ml-2" {...props} />,
                          strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                          em: ({node, ...props}) => <em className="italic" {...props} />,
                          code: ({node, ...props}) => <code className="bg-gray-100 px-1 rounded text-xs" {...props} />,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))
            )}
            {loading.chat && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <p className="text-sm text-gray-600">Thinking...</p>
                </div>
              </div>
            )}
          </div>
          <form onSubmit={handleSendChat} className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask me anything..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                disabled={loading.chat}
              />
              <button
                type="submit"
                disabled={loading.chat || !chatInput.trim()}
                className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}

      {/* PowerPoint Preview Modal */}
      {showPPTPreview && pitchDeckResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-xl flex items-center justify-between">
              <h3 className="text-xl font-semibold">PowerPoint Preview</h3>
              <button
                onClick={() => setShowPPTPreview(false)}
                className="text-white hover:text-gray-200 text-2xl"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              {previewSlides && previewSlides.length > 0 ? (
                <div className="space-y-4">
                  {previewSlides.map((slide, idx) => (
                    <div key={idx} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold">
                          Slide {slide.slide_number || idx + 1}
                        </span>
                        <h4 className="font-semibold text-gray-800">{slide.title}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{slide.content}</p>
                      {slide.key_points && slide.key_points.length > 0 && (
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {slide.key_points.map((point, pIdx) => (
                            <li key={pIdx}>{point}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No slides to preview</p>
              )}
            </div>
            <div className="border-t border-gray-200 p-4 flex gap-3">
              <button
                onClick={() => {
                  let filename = pitchDeckResult.pptx_path;
                  filename = filename.replace(/^exports[/\\]/, '');
                  filename = filename.split('/').pop() || filename.split('\\').pop();
                  filename = filename.replace(/^.*[/\\]/, '');
                  handleDownloadPPT(filename);
                }}
                className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all font-medium"
              >
                Download PowerPoint
              </button>
              <button
                onClick={() => setShowPPTPreview(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agent Form Modal */}
      {showForm && (
        <AgentForm
          questionnaire={formQuestionnaire}
          title={formTitle}
          onClose={() => {
            setShowForm(false);
            setFormType(null);
            setFormQuestionnaire([]);
          }}
          onSubmit={handleFormSubmit}
          loading={loading[formType]}
        />
      )}

      {/* Agent Form Modal */}
      {showForm && (
        <AgentForm
          questionnaire={formQuestionnaire}
          title={formTitle}
          onClose={() => {
            setShowForm(false);
            setFormType(null);
            setFormQuestionnaire([]);
          }}
          onSubmit={handleFormSubmit}
          loading={loading[formType]}
        />
      )}

      {/* Chat Button (Floating) */}
      {!showChat && (
        <button
          onClick={() => setShowChat(true)}
          className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-violet-600 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center gap-2 z-40"
        >
          <span>💬</span>
          <span className="font-medium">Ask me anything</span>
        </button>
      )}
    </div>
  );
};

export default Dashboard;
