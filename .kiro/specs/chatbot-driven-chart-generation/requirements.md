# Requirements Document

## Introduction

This document specifies requirements for redesigning the SF CHAI chart generation workflow from a one-click button approach to a conversational chatbot-driven workflow. The current implementation produces charts with accuracy issues (missing legends, incorrect annotations, wrong positioning) because users have no visibility or control before generation. The new chatbot workflow will present a detailed analysis and proposal for user review and approval before chart generation, enabling users to correct AI misunderstandings and validate mappings conversationally.

## Glossary

- **Chart_Generator**: The system component responsible for creating chart visualizations from CSV data and reference images
- **Chatbot**: The conversational interface component that guides users through the chart generation workflow
- **Analysis_Proposal**: A structured presentation of how the system intends to map data and configure visual elements
- **CSV_File**: A comma-separated values file containing the data to be visualized
- **Reference_Image**: An image file showing the desired chart style and layout
- **Data_Mapping**: The association between CSV columns and chart series/elements
- **Visual_Configuration**: The set of visual properties including colors, fonts, legend placement, and annotations
- **Session**: A persistent workspace containing uploaded files, proposals, and generated charts

## Requirements

### Requirement 1: Upload Files Through Chat Interface

**User Story:** As a user, I want to upload my CSV data file and reference image through the chat interface, so that I can initiate the chart generation workflow conversationally.

#### Acceptance Criteria

1. WHEN a user sends a CSV_File through the Chatbot, THE Chatbot SHALL accept the file and confirm receipt
2. WHEN a user sends a Reference_Image through the Chatbot, THE Chatbot SHALL accept the file and confirm receipt
3. THE Chatbot SHALL accept CSV_File and Reference_Image in any order
4. WHEN both CSV_File and Reference_Image are uploaded, THE Chatbot SHALL proceed to analysis
5. IF a CSV_File is uploaded without required data columns, THEN THE Chatbot SHALL return a descriptive error message

### Requirement 2: Analyze Files and Generate Proposal

**User Story:** As a user, I want the system to analyze my files and present a detailed proposal, so that I can understand how my data will be visualized before generation.

#### Acceptance Criteria

1. WHEN both CSV_File and Reference_Image are uploaded, THE Chart_Generator SHALL analyze both files
2. THE Chart_Generator SHALL produce an Analysis_Proposal containing data mapping, visual configuration, legend configuration, and annotation specifications
3. THE Chatbot SHALL present the Analysis_Proposal in structured natural language format
4. THE Analysis_Proposal SHALL specify which CSV columns map to which chart series
5. THE Analysis_Proposal SHALL specify colors, line styles, and smoothness for each series
6. THE Analysis_Proposal SHALL specify legend type, position, and font size
7. THE Analysis_Proposal SHALL specify all annotations including horizontal lines, vertical lines, and shaded bands with exact values
8. THE Analysis_Proposal SHALL specify fonts and sizes for all text elements
9. THE Analysis_Proposal SHALL specify grid and spacing configuration

### Requirement 3: Present Proposal in Human-Readable Format

**User Story:** As a user, I want the proposal presented in clear, structured language rather than technical formats, so that I can easily understand and review the planned visualization.

#### Acceptance Criteria

1. THE Chatbot SHALL present the Analysis_Proposal using natural language descriptions
2. THE Chatbot SHALL organize the Analysis_Proposal into logical sections
3. THE Chatbot SHALL avoid presenting raw JSON or technical data structures to the user
4. THE Chatbot SHALL use consistent terminology from the Glossary when presenting proposals

### Requirement 4: Enable User Review and Modification

**User Story:** As a user, I want to review the proposal and request changes through conversation, so that I can correct AI misunderstandings before chart generation.

#### Acceptance Criteria

1. WHEN an Analysis_Proposal is presented, THE Chatbot SHALL wait for user approval before generating the chart
2. THE Chatbot SHALL accept natural language modification requests
3. WHEN a user requests a change to the Analysis_Proposal, THE Chatbot SHALL update the proposal and present the modified version
4. THE Chatbot SHALL accept modification requests for data mapping, colors, legend placement, annotations, fonts, and spacing
5. THE Chatbot SHALL allow multiple iterative modifications before generation
6. WHEN a user asks questions about the Analysis_Proposal, THE Chatbot SHALL provide clarifying explanations

### Requirement 5: Generate Chart Upon Explicit Approval

**User Story:** As a user, I want to explicitly approve the proposal before chart generation, so that I have control over when the chart is created.

#### Acceptance Criteria

1. THE Chart_Generator SHALL generate a chart only after user approval
2. WHEN a user approves an Analysis_Proposal, THE Chart_Generator SHALL create the chart according to the proposal specifications
3. WHEN chart generation completes, THE Chatbot SHALL present the generated chart to the user
4. IF chart generation fails, THEN THE Chatbot SHALL return a descriptive error message and maintain the Analysis_Proposal for modification

### Requirement 6: Support Post-Generation Refinement

**User Story:** As a user, I want to request modifications to the generated chart through conversation, so that I can refine the visualization iteratively.

#### Acceptance Criteria

1. WHEN a chart is generated, THE Chatbot SHALL accept modification requests
2. WHEN a user requests a modification to a generated chart, THE Chart_Generator SHALL update the chart according to the request
3. THE Chatbot SHALL accept natural language modification requests for all visual elements
4. THE Chart_Generator SHALL preserve the current chart state between modifications

### Requirement 7: Maintain Session Persistence

**User Story:** As a user, I want my uploaded files, proposals, and generated charts saved in a session, so that I can return to my work later.

#### Acceptance Criteria

1. THE Chart_Generator SHALL maintain a Session containing uploaded files, Analysis_Proposal, and generated charts
2. THE Chart_Generator SHALL support saving a Session to persistent storage
3. THE Chart_Generator SHALL support loading a previously saved Session
4. WHEN a Session is loaded, THE Chatbot SHALL restore the conversation context and display the current state

### Requirement 8: Preserve Existing Chart Rendering Capabilities

**User Story:** As a developer, I want to maintain the current chart rendering and modification capabilities, so that existing functionality continues to work.

#### Acceptance Criteria

1. THE Chart_Generator SHALL preserve all existing chart rendering capabilities
2. THE Chart_Generator SHALL preserve all existing chart modification capabilities
3. THE Chart_Generator SHALL support all chart types currently supported
4. THE Chart_Generator SHALL maintain compatibility with existing chart data formats

### Requirement 9: Handle Conversational Interactions

**User Story:** As a user, I want to interact with the system using natural language, so that I don't need to learn technical commands or syntax.

#### Acceptance Criteria

1. THE Chatbot SHALL parse natural language user inputs
2. THE Chatbot SHALL recognize approval phrases such as "looks good", "generate it", "approve"
3. THE Chatbot SHALL recognize modification requests such as "change the color to red", "move legend to bottom"
4. THE Chatbot SHALL recognize questions about the Analysis_Proposal
5. IF the Chatbot cannot understand a user input, THEN THE Chatbot SHALL ask for clarification

### Requirement 10: Validate Data Mapping Accuracy

**User Story:** As a user, I want to validate that CSV columns are correctly mapped to chart elements, so that I can ensure data accuracy before generation.

#### Acceptance Criteria

1. THE Analysis_Proposal SHALL explicitly state which CSV column maps to each chart series
2. THE Analysis_Proposal SHALL include sample values from each mapped column
3. WHEN a user questions a data mapping, THE Chatbot SHALL explain the reasoning for the mapping
4. THE Chatbot SHALL accept user corrections to data mappings before chart generation
