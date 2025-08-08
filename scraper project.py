import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ----- Trie Data Structure -----
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.sentences = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, sentence):
        node = self.root
        for char in sentence.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.sentences.append(sentence)
        node.is_end = True

    def search(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char in node.children:
                node = node.children[char]
            else:
                return []
        return list(dict.fromkeys(node.sentences))[:10]  # Remove duplicates and return top 10

# ----- Global Trie -----
trie = Trie()

# ----- Scraping and Categorizing Function -----
def scrape_website(query, website_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(website_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching website: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])

    # HashMap to categorize data
    categorized_results = {"h1": [], "h2": [], "h3": [], "p": [], "li": []}

    for element in text_elements:
        tag = element.name
        text = element.get_text(strip=True)
        if query.lower() in text.lower():
            categorized_results[tag].append(text)
            trie.insert(text)  # Insert into Trie for future prefix search

    return categorized_results

# ----- GUI Action -----
def on_scrape():
    sentence = entry_sentence.get().strip()
    website = entry_website.get().strip()
    text_output.delete(1.0, tk.END)

    if not sentence or not website:
        messagebox.showwarning("Input Error", "Please enter both search sentence and website URL.")
        return

    results = scrape_website(sentence, website)
    if isinstance(results, str):
        text_output.insert(tk.END, results)
        return

    has_results = False
    for tag, texts in results.items():
        if texts:
            has_results = True
            text_output.insert(tk.END, f"=== {tag.upper()} TAG RESULTS ===\n")
            for idx, text in enumerate(texts, 1):
                text_output.insert(tk.END, f"{idx}. {text}\n")
            text_output.insert(tk.END, "\n")

    if not has_results:
        text_output.insert(tk.END, "No relevant information found.")

# ----- Prefix Search -----
def on_prefix_search():
    prefix = entry_prefix.get().strip()
    text_output.delete(1.0, tk.END)
    if not prefix:
        messagebox.showinfo("Input Needed", "Enter a word/prefix to search.")
        return
    results = trie.search(prefix)
    if results:
        text_output.insert(tk.END, f"Top matches for prefix '{prefix}':\n\n")
        for idx, res in enumerate(results, 1):
            text_output.insert(tk.END, f"{idx}. {res}\n\n")
    else:
        text_output.insert(tk.END, "No matches found in stored sentences.")

# ----- GUI Setup -----
root = tk.Tk()
root.title("Website Scraper with DSA")
root.geometry("800x600")

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

# Scrape Input
tk.Label(frame_input, text="Search Sentence:").grid(row=0, column=0, sticky="e", padx=5)
entry_sentence = tk.Entry(frame_input, width=60)
entry_sentence.grid(row=0, column=1)

tk.Label(frame_input, text="Website URL:").grid(row=1, column=0, sticky="e", padx=5)
entry_website = tk.Entry(frame_input, width=60)
entry_website.grid(row=1, column=1)

btn_scrape = tk.Button(root, text="Scrape", command=on_scrape, bg="blue", fg="white")
btn_scrape.pack(pady=5)

# Prefix Search
frame_prefix = tk.Frame(root)
frame_prefix.pack(pady=5)

tk.Label(frame_prefix, text="Prefix Search:").grid(row=0, column=0, sticky="e", padx=5)
entry_prefix = tk.Entry(frame_prefix, width=40)
entry_prefix.grid(row=0, column=1)
btn_search_prefix = tk.Button(frame_prefix, text="Search Prefix", command=on_prefix_search, bg="green", fg="white")
btn_search_prefix.grid(row=0, column=2, padx=5)

# Output
text_output = scrolledtext.ScrolledText(root, width=95, height=25, wrap=tk.WORD)
text_output.pack(padx=10, pady=10)

root.mainloop()
