import os
import subprocess
from typing import Optional
from openai.types.chat import ChatCompletion

from git_commit_bot.providers import chatgpt_client
from git_commit_bot.models import DiffInfo

def get_git_diff() -> Optional[DiffInfo]:
    """Get the diff of staged changes in the git repository."""
    try:
        # Get list of changed files
        files_cmd = ["git", "diff", "--name-only", "--staged"]
        files_output = subprocess.check_output(files_cmd, text=True)
        
        if not (
            files_changed := files_output.strip().split('\n') if files_output.strip() else []
        ):
            # Check if we have staged new files in a new repo
            if (staged_new_files := _check_for_new_files()):
                # For new files, get their entire content as the diff
                diff_content = []
                for file in staged_new_files:
                    try:
                        with open(file, 'r') as f:
                            content = f.read()
                            diff_content.append(f'New file: {file}\n{content}')
                    except Exception as e:
                        print(f"Error reading file {file}: {e}")
                
                return DiffInfo(
                    files_changed=staged_new_files,
                    diff_content='\n'.join(diff_content)
                )
            return None
            
        # Get the actual diff content
        diff_cmd = ["git", "diff", "--staged"]
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
    
    prompt = f"""Given the following git diff, please generate a clear, concise and meaningful commit message 
    that follows conventional commit format (e.g., feat:, fix:, refactor:, etc.).
    The message should be no more than 72 characters for the first line, followed by a more detailed
    description if necessary.
    
    Changed files: {', '.join(diff_info.files_changed)}
    
    Diff content:
    {diff_info.diff_content}
    """
    
    try:
        response: ChatCompletion = chatgpt_client.completions.create(
            model="gpt-4",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates clear, concise and meaningful git commit messages based on diffs."},
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

def _check_for_new_files() -> list[str]:
    """Check for new files in the git repository."""
    status_cmd = ["git", "status", "--porcelain"]
    status_output = subprocess.check_output(status_cmd, text=True)

    return [
        line[3:] for line in status_output.split('\n')
        if line.startswith('A  ') or line.startswith('M  ')
    ]

if __name__ == "__main__":
    main()