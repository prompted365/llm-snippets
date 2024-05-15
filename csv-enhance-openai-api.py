import openai
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize your OpenAI client
openai.api_key = 'your-api-key'
client = openai.OpenAI(api_key=openai.api_key)

# Function to create a thread and add a message
def create_thread(question):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )
    return thread.id

# Define an event handler class for streaming responses
class EventHandler(AssistantEventHandler):    
    @override
    def on_text_created(self, text):
        print(f"\nassistant > ", end="", flush=True)
      
    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
      
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)
  
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

# Load your dataset
data = pd.read_csv('path_to_your_dataset.csv')

# Iterate through the dataset
for index, row in data.iterrows():
    question = row['q']
    thread_id = create_thread(question)
    
    # Stream the response using the EventHandler
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id='your-assistant-id',  # specify the assistant id
        instructions="Generate a detailed, accurate response adhering to the context.",
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()

    # Here you would typically collect the response and update your dataset
    # Since printing is done in real-time, you might want to adjust this part to capture responses.

# Save the updated dataset after all entries are processed
data.to_csv('updated_dataset.csv', index=False)