# run_local_demo.py
from modules.coordinator import Coordinator
def main():
    c = Coordinator()
    s = c.start_session(user_id="charan", topic="deep work", tone="conversational", keywords=["productivity"])
    out = c.run(s)
    print("SUMMARY TYPE:", type(out))
    if isinstance(out, dict):
        if out.get("final_markdown"):
            print("FINAL MARKDOWN LEN:", len(out["final_markdown"]))
        else:
            print("DRAFT TITLE:", out.get("title"))
if __name__ == "__main__":
    main()
