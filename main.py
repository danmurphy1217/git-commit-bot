import os
import subprocess
from typing import Optional
import openai
from openai.types.chat import ChatCompletion
from dataclasses import dataclass

@dataclass
class DiffInfo:
    files_changed: list[str]
    diff_content: str
    
def get_git_diff() -> Optional[DiffInfo]:
    """Get the diff of staged changes in the git repository."""
    try:
        # Get list of changed files
        files_cmd = ["git", "diff", "--name-only"]
        files_output = subprocess.check_output(files_cmd, text=True)
        files_changed = files_output.strip().split('\n') if files_output.strip() else []
        
        if not files_changed:
            return None
            
        # Get the actual diff content
        diff_cmd = ["git", "diff", "--cached"]
        diff_output = subprocess.check_output(diff_cmd, text=True)
        
        return DiffInfo(
            files_changed=files_changed,
            diff_content=diff_output
        )
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git is not installed")
        return None

def generate_commit_message(diff_info: DiffInfo, api_key: str) -> str:
    """Generate a commit message using GPT based on the diff content."""
    openai.api_key = api_key
    
    prompt = f"""Given the following git diff, please generate a clear and concise commit message 
    that follows conventional commit format (e.g., feat:, fix:, refactor:, etc.).
    The message should be no more than 72 characters for the first line, followed by a more detailed
    description if necessary.
    
    Changed files: {', '.join(diff_info.files_changed)}
    
    Diff content:
    {diff_info.diff_content}
    """
    
    try:
        response: ChatCompletion = openai.chat.completions.create(
            model="gpt-4",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates clear and meaningful git commit messages based on diffs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        first_message_content = response.choices[0].message.content
        if not first_message_content:
            raise Exception("No content in response")
        
        return first_message_content.strip()
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return ""

def main():
    """Main function to run the commit message generator."""
    # Get OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Get the diff information
    diff_info = get_git_diff()
    if not diff_info:
        print("No staged changes found. Stage your changes using 'git add' first.")
        return
    
    # Generate commit message
    commit_message = generate_commit_message(diff_info, api_key)
    if not commit_message:
        print("Failed to generate commit message")
        return
        
    print("\nSuggested commit message:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    # Ask user if they want to use this message
    user_input = input("\nDo you want to use this commit message? (y/n): ")
    if user_input.lower() == 'y':
        try:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("Changes committed successfully!")
        except subprocess.CalledProcessError:
            print("Error: Failed to commit changes")
    else:
        print("Commit cancelled")

if __name__ == "__main__":
    main()