import React, { useState } from 'react';
import { useApp } from '../store/AppContext';
import { Download, FileText, ChevronDown, ChevronUp } from 'lucide-react';

const ActivityPanel: React.FC = () => {
  const { activities, company } = useApp();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();
    
    if (isToday) {
      return 'Today';
    }
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  const getToolIcon = (type: string) => {
    const icons: Record<string, string> = {
      pitch: '🎯',
      elevator: '🗣️',
      competitive: '📊',
      marketing: '📱',
      policy: '📋',
      patent: '💡',
      team: '👥',
      chat: '💬',
    };
    return icons[type] || '📝';
  };

  const getToolName = (type: string) => {
    const names: Record<string, string> = {
      pitch: 'Pitch Deck Generator',
      elevator: 'Elevator Pitch',
      competitive: 'Competitive Analysis',
      marketing: 'Marketing Content',
      policy: 'Policy Generator',
      patent: 'Patent Analysis',
      team: 'Team Analysis',
      chat: 'AI Chat',
    };
    return names[type] || 'AI Tool';
  };

  // Sort activities by timestamp (newest first)
  const sortedActivities = [...activities].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  // Get activities with content for download
  const activitiesWithContent = sortedActivities.filter(a => a.content);

  const generateReport = () => {
    const now = new Date();
    const reportDate = now.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    // Build an HTML report that opens nicely in Word
    const companyName = company?.company_name || 'Unknown';
    const toolList = [...new Set(sortedActivities.map(a => getToolName(a.type)))];

    const activityCards = activitiesWithContent
      .map((activity, index) => {
        const activityDate = new Date(activity.timestamp).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
        });
        const safeContent = (activity.content || '').replace(/\\n/g, '<br/>');
        return `
          <div class="card">
            <div class="card-header">
              <div class="title">${index + 1}. ${activity.title}</div>
              <div class="pill">${getToolName(activity.type)}</div>
            </div>
            <div class="meta">Generated: ${activityDate}</div>
            <div class="meta">Description: ${activity.description}</div>
            <div class="content" aria-label="Generated Content">${safeContent}</div>
          </div>
        `;
      })
      .join('');

    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>TechScopeAI Report</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #1f2937; margin: 32px; }
    h1 { color: #6b21a8; margin-bottom: 4px; }
    h2 { color: #312e81; border-bottom: 2px solid #e5e7eb; padding-bottom: 4px; }
    .subtitle { color: #6b7280; margin-bottom: 24px; }
    .section { margin-top: 24px; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-top: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .title { font-size: 16px; font-weight: 700; color: #111827; }
    .pill { background: linear-gradient(135deg, #7c3aed, #db2777); color: white; padding: 6px 10px; border-radius: 999px; font-size: 12px; }
    .meta { color: #6b7280; font-size: 12px; margin-bottom: 4px; }
    .content { margin-top: 8px; line-height: 1.6; white-space: pre-wrap; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .info { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; }
    .label { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
    .value { font-weight: 600; color: #111827; margin-top: 2px; }
    .summary-list { margin-top: 8px; color: #374151; }
  </style>
</head>
<body>
  <h1>TechScopeAI Report</h1>
  <div class="subtitle">Generated on ${reportDate}</div>

  <div class="section">
    <h2>Company Profile</h2>
    <div class="grid">
      <div class="info"><div class="label">Company</div><div class="value">${companyName}</div></div>
      <div class="info"><div class="label">Industry</div><div class="value">${company?.industry || 'Unknown'}</div></div>
      <div class="info"><div class="label">Stage</div><div class="value">${company?.current_stage || 'N/A'}</div></div>
      <div class="info"><div class="label">Traction</div><div class="value">${company?.traction || 'N/A'}</div></div>
      <div class="info"><div class="label">Funding Goal</div><div class="value">${company?.funding_goal || 'N/A'}</div></div>
    </div>
    <div class="card" style="margin-top:16px;">
      <div class="label">Problem Statement</div>
      <div class="content">${(company?.problem || 'N/A').replace(/\\n/g, '<br/>')}</div>
      <div class="label" style="margin-top:12px;">Solution</div>
      <div class="content">${(company?.solution || 'N/A').replace(/\\n/g, '<br/>')}</div>
      <div class="label" style="margin-top:12px;">Target Market</div>
      <div class="content">${(company?.target_market || 'N/A').replace(/\\n/g, '<br/>')}</div>
      <div class="label" style="margin-top:12px;">Unique Value Proposition</div>
      <div class="content">${(company?.solution || 'N/A').replace(/\\n/g, '<br/>')}</div>
    </div>
  </div>

  <div class="section">
    <h2>Generated Content</h2>
    ${activitiesWithContent.length > 0 ? activityCards : '<div class="info">No content generated yet.</div>'}
  </div>

  <div class="section">
    <h2>Session Summary</h2>
    <div class="grid">
      <div class="info">
        <div class="label">Total Activities</div>
        <div class="value">${sortedActivities.length}</div>
      </div>
      <div class="info">
        <div class="label">With Content</div>
        <div class="value">${activitiesWithContent.length}</div>
      </div>
    </div>
    <div class="summary-list">
      <div class="label" style="margin-top:12px;">Tools Used</div>
      <ul>
        ${toolList.map(tool => `<li>${tool}</li>`).join('')}
      </ul>
    </div>
  </div>
</body>
</html>
`;

    // Download the report as a Word-friendly document
    const blob = new Blob([html], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TechScopeAI_Report_${companyName.replace(/\\s+/g, '_')}_${now.toISOString().split('T')[0]}.doc`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="activity-panel p-6 h-[calc(100vh-100px)] flex flex-col rounded-2xl">
      {/* Header */}
      <div className="mb-4 pb-4 border-b border-purple-800/30">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Activity Report</h2>
            <p className="text-sm text-purple-300 mt-1">Your generated content</p>
          </div>
          {activitiesWithContent.length > 0 && (
            <button
              onClick={generateReport}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-purple-500/30 transition-all"
            >
              <Download size={16} />
              <span>Download Report</span>
            </button>
          )}
        </div>
        {activitiesWithContent.length > 0 && (
          <p className="text-xs text-purple-400 mt-2">
            {activitiesWithContent.length} item{activitiesWithContent.length > 1 ? 's' : ''} ready for download
          </p>
        )}
      </div>

      {/* Activities */}
      <div className="flex-1 overflow-y-auto dark-panel pr-2">
        {sortedActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-800/50 to-purple-900/50 flex items-center justify-center mb-6 shadow-lg">
              <FileText className="w-12 h-12 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">No Activity Yet</h3>
            <p className="text-purple-300 text-sm leading-relaxed max-w-[220px]">
              Your generated content will appear here. Use any tool to get started!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedActivities.map((activity, index) => (
              <div
                key={activity.id || index}
                className="bg-purple-900/30 rounded-xl border border-purple-700/30 overflow-hidden transition-all hover:bg-purple-900/40"
              >
                {/* Activity Header */}
                <div 
                  className="p-4 cursor-pointer"
                  onClick={() => activity.content && toggleExpand(activity.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{getToolIcon(activity.type)}</span>
                      <span className="font-semibold text-white text-sm">
                        {activity.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-purple-400 whitespace-nowrap bg-purple-800/50 px-2 py-1 rounded-full">
                        {formatTime(activity.timestamp)}
                      </span>
                      {activity.content && (
                        expandedId === activity.id 
                          ? <ChevronUp size={16} className="text-purple-400" />
                          : <ChevronDown size={16} className="text-purple-400" />
                      )}
                    </div>
                  </div>
                  
                  <p className="text-purple-200 text-sm">
                    {activity.description}
                  </p>
                  
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-purple-400">
                      {formatDate(activity.timestamp)}
                    </span>
                    <span className="text-xs text-purple-500 bg-purple-900/50 px-2 py-0.5 rounded">
                      {getToolName(activity.type)}
                    </span>
                  </div>
                </div>

                {/* Expanded Content Preview */}
                {activity.content && expandedId === activity.id && (
                  <div className="border-t border-purple-700/30 bg-purple-950/50 p-4">
                    <div className="text-xs text-purple-300 font-medium mb-2">Content Preview:</div>
                    <div className="text-purple-200 text-xs leading-relaxed max-h-40 overflow-y-auto bg-purple-900/30 p-3 rounded-lg">
                      {activity.content.substring(0, 500)}
                      {activity.content.length > 500 && '...'}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      {sortedActivities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-purple-800/30">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-purple-900/30 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-white">{sortedActivities.length}</div>
              <div className="text-xs text-purple-400">Total Activities</div>
            </div>
            <div className="bg-purple-900/30 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-white">{activitiesWithContent.length}</div>
              <div className="text-xs text-purple-400">With Content</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityPanel;
