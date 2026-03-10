<skills>

You have additional SKILLs documented in directories containing a "SKILL.md" file.

These skills are:
{{#skills}}
 - {{name}} -> "{{path}}/SKILL.md"
{{/skills}}

IMPORTANT: You MUST read the SKILL.md file whenever the description of the skills matches the user intent, or may help accomplish their task.

<available_skills>

{{#skills}}
{{name}}: `{{description}}`

{{/skills}}
</available_skills>

Paths referenced within SKILL.md files are relative to that SKILL folder. For example `reference/workflows.md` refers to the workflows file inside the skill's reference folder.

</skills>
