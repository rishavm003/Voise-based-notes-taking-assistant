import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Dataset configuration
VOCAB_SIZE = 6000
MAX_LENGTH = 60
EMBEDDING_DIM = 128

def get_dataset():
    # label 0: work, 1: personal, 2: idea, 3: reminder
    data = []

    # WORK (80 examples)
    work = [
        "schedule team standup for monday 10am",
        "send invoice to the client by end of day",
        "review pull request number 47 from the dev team",
        "deadline for the product launch is next friday",
        "follow up with hr about the onboarding process",
        "prepare slides for the investor presentation tomorrow",
        "update the project tracker in jira with today's progress",
        "call the vendor about the delayed shipment",
        "email the quarterly report to the finance department",
        "book a conference room for the architecture workshop",
        "discuss the marketing strategy with the sales team",
        "fix the critical bug in the payment gateway module",
        "respond to the customer support tickets by noon",
        "write a summary of the stakeholder meeting notes",
        "coordinate the release schedule with the devops team",
        "analyze the server logs for the production error",
        "submit the budget proposal for the next fiscal year",
        "interview the candidate for the senior engineer role",
        "update the technical documentation on the internal wiki",
        "present the project roadmap to the executive committee",
        "request access to the staging environment for testing",
        "organize the files in the shared project directory",
        "set up a meeting with the design team for the ui review",
        "draft the contract for the new service provider",
        "review the security audit findings and plan fixes",
        "sync with the backend team about the api integration",
        "prepare for the technical demo at the town hall",
        "write the unit tests for the authentication service",
        "attend the daily scrum meeting at 9:30 am sharp",
        "evaluate the new framework for the mobile app project",
        "document the steps for the local environment setup",
        "automate the deployment pipeline using github actions",
        "refactor the legacy code in the data processing layer",
        "monitor the system performance after the latest update",
        "configure the alerts for the cloud infrastructure",
        "discuss the product requirements with the business owner",
        "send the meeting agenda to all attendees in advance",
        "update the team on the status of the current sprint",
        "review the pull requests from the junior developers",
        "plan the tasks for the upcoming development cycle",
        "manage the cloud costs on the aws console",
        "implement the rate limiting for the public endpoints",
        "standardize the logging format across all services",
        "conduct the code quality review for the main repo",
        "streamline the onboarding for the new team members",
        "investigate the reported latency in the database",
        "develop a prototype for the voice command feature",
        "research the best practices for microservices security",
        "draft the email announcement for the system maintenance",
        "schedule a demo of the new analytics dashboard",
        "review the feedback from the beta testers session",
        "update the dependencies in the root package file",
        "create a backup of the production database nightly",
        "monitor the error rates in the monitoring dashboard",
        "configure the load balancer for the scaling group",
        "discuss the system architecture with the lead architect",
        "write the integration tests for the search api",
        "perform the load testing for the holiday season prep",
        "set up the continuous integration for the new repo",
        "manage the project tasks on the kanban board",
        "troubleshoot the connectivity issues with the cache",
        "implement the role based access control for the portal",
        "audit the api keys and environment variables usage",
        "refactor the database schema for better performance",
        "design the user interface for the admin panel",
        "integrate the third party logging service into app",
        "write the release notes for the upcoming version",
        "coordinate the user testing with the qa department",
        "optimize the asset loading for the landing page",
        "implement the localization for the european market",
        "set up the ssl certificates for the new domain",
        "configure the firewall rules for the virtual network",
        "review the performance of the search indexing job",
        "implement the caching strategy for the dashboard",
        "write the documentation for the internal sdk",
        "analyze the user engagement data from the last week",
        "prepare the budget report for the management sync",
        "discuss the feature prioritization for next month",
        "write the technical spec for the migration project",
        "review the legal terms for the data processing"
    ]
    data.extend([(text, 0) for text in work])

    # PERSONAL (80 examples)
    personal = [
        "buy groceries tonight milk eggs bread and onions",
        "call mom sunday it is her birthday next week",
        "dentist appointment on tuesday at 11am dont forget",
        "pay electricity bill before the 15th or get fine",
        "pick up dry cleaning from the shop near office",
        "book flight tickets for the december vacation",
        "go for a run three times this week morning",
        "renew car insurance before the end of the month",
        "clean the apartment on saturday morning thoroughly",
        "visit the gallery exhibition with sarah this weekend",
        "buy a birthday gift for lily from the mall",
        "check the expiration date of the milk in fridge",
        "update the workout routine for the upcoming week",
        "send a thank you note to the hosts of the dinner",
        "water the plants in the balcony twice a week",
        "recharge the metro card before the balance is zero",
        "take the dog for a long walk in the park sunday",
        "watch the latest episode of the favorite series",
        "organize the photos from the last summer trip",
        "call the insurance company about the claim status",
        "prepare a healthy meal for dinner with fresh greens",
        "visit the library to return the borrowed books",
        "check the weather forecast for the weekend hike",
        "buy a new charging cable for the phone today",
        "schedule a haircut for next wednesday afternoon",
        "plan a surprise dinner for marks graduation day",
        "write a journal entry about the week experiences",
        "practice the guitar for an hour every evening",
        "cancel the gym membership before the next billing",
        "take the car for the annual service at the garage",
        "buy some flowers for the living room decoration",
        "call dad to check on his health after the surgery",
        "organize the wardrobe and donate the old clothes",
        "try the new recipe for the homemade pasta sauce",
        "book a yoga class for the saturday morning session",
        "check the bank statement for the last month spending",
        "renew the subscription for the streaming platform",
        "buy a new diary for the upcoming new year",
        "clean the windows and the mirrors in the house",
        "plan a weekend trip to the mountains with friends",
        "rearrange the furniture in the bedroom for change",
        "bake some cookies for the neighbors this weekend",
        "check the pressure in the car tires before drive",
        "buy some stationery items like pens and notebooks",
        "set a budget for the monthly grocery shopping trip",
        "visit the local farmers market on sunday morning",
        "listen to a meditation podcast before going to bed",
        "update the contact list with the new phone numbers",
        "plan the outfits for the next week to save time",
        "wash the bedsheets and the towels on the weekend",
        "buy some healthy snacks for the office work day",
        "call the plumber to fix the leak in the kitchen",
        "write a list of things to pack for the beach trip",
        "clean the filter of the air conditioner today",
        "try the new cafe that opened around the corner",
        "take a nap for twenty minutes in the afternoon",
        "buy a new light bulb for the study desk lamp",
        "check the garden for any pests and remove them",
        "plan a picnic at the lake if it is sunny sunday",
        "recharge the battery of the camera for the event",
        "buy some seasonal fruits from the local vendor",
        "organize the documents in the home filing cabinet",
        "call a friend from college to catch up this week",
        "read a few chapters of the historical fiction book",
        "buy some olive oil and balsamic vinegar for salad",
        "clean the bathroom tiles and the shower area",
        "plan a movie marathon for the friday night in",
        "update the personal blog with a travel story",
        "check the balance of the rewards card at store",
        "buy a new pair of comfortable walking shoes",
        "organize the spices in the kitchen shelf properly",
        "take some sunset photos from the rooftop today",
        "call the electrician to fix the broken wall socket",
        "write down the dreams in the morning dream diary",
        "buy some eco friendly cleaning products for home",
        "plan a volunteer session at the local animal shelter",
        "check the pantry for any items that need restocking",
        "renew the library card before it expires next week",
        "buy some fresh herbs like basil and parsley",
        "organize the tools in the garage on sunday afternoon"
    ]
    data.extend([(text, 1) for text in personal])

    # IDEA (80 examples)
    idea = [
        "app idea that tracks your daily water intake with reminders",
        "new feature for the platform add voice search option",
        "business concept subscription box for local handmade crafts",
        "startup idea connecting freelancers with small businesses",
        "blog post about the future of ai in healthcare sector",
        "game mechanic where players solve logic puzzles to progress",
        "product idea reusable smart label for food containers",
        "research topic comparing transformer models on edge devices",
        "concept for a browser extension that summarizes long videos",
        "idea for a mobile game about building sustainable cities",
        "new business model for a peer to peer tool rental service",
        "feature idea for the app collaborative voice note folders",
        "concept for a smart mirror that suggests outfits based on weather",
        "startup concept a platform for sharing unused office space",
        "idea for a wearable device that tracks indoor air quality",
        "new way to visualize personal finance data using 3d charts",
        "concept for an automated garden system for urban apartments",
        "feature to automatically generate mind maps from voice notes",
        "idea for a smart backpack with integrated gps and solar charging",
        "concept for a marketplace for digital assets for virtual worlds",
        "startup idea providing personalized career coaching using ai",
        "feature to extract action items from audio meetings automatically",
        "concept for a subscription service for high end camera gear",
        "idea for a mobile app that helps identify local bird species",
        "new way to experience museum tours using augmented reality",
        "concept for a sustainable fashion brand using mushroom leather",
        "startup idea connecting local farmers directly with consumers",
        "feature to set geofenced reminders for specific voice notes",
        "idea for an ergonomic workspace that adapts to posture",
        "concept for a community driven library of physical books",
        "startup idea providing affordable mental health support online",
        "feature to translate voice notes in real time during playback",
        "idea for a smart kitchen scale that tracks nutritional values",
        "concept for a decentralized social network for scientists",
        "startup idea offering custom 3d printed orthotics at home",
        "feature to analyze the sentiment and tone of voice notes",
        "idea for a smart lock that uses multi factor authentication",
        "concept for a zero waste grocery store with robotic dispensers",
        "startup idea providing personalized education plans for kids",
        "feature to integrate voice notes with smart home systems",
        "idea for a portable water purifier using advanced uv technology",
        "concept for a virtual reality platform for remote team building",
        "startup idea creating biodegradable alternatives to plastic",
        "feature to automatically categorize notes using deep learning",
        "idea for a smart bike helmet with integrated turn signals",
        "concept for a platform that rewards users for sustainable habits",
        "startup idea providing on demand repair services for gadgets",
        "feature to create interactive audio stories from simple notes",
        "idea for a smart pillow that optimizes sleep based on biofeedback",
        "concept for a marketplace for unused gift cards and vouchers",
        "startup idea connecting students with professional mentors",
        "feature to visualize the connections between related ideas",
        "idea for a smart waste bin that tracks and rewards recycling",
        "concept for a subscription based platform for high end art",
        "startup idea offering personalized travel itineraries using ai",
        "feature to add emotional context to transcripts using ai",
        "idea for a smart thermostat that predicts energy needs",
        "concept for a platform for sharing and renting outdoor equipment",
        "startup idea providing mobile car detailing services at home",
        "feature to generate automated summaries for long recordings",
        "idea for a smart mirror for fitness with real time form correction",
        "concept for a sustainable energy grid managed by the community",
        "startup idea providing custom meal plans based on dna testing",
        "feature to share voice notes securely using blockchain technology",
        "idea for a smart cane for the visually impaired with lidar",
        "concept for a virtual personal assistant for elderly people",
        "startup idea offering localized weather predictions for farmers",
        "feature to integrate voice notes with popular productivity apps",
        "idea for a smart yoga mat that tracks pressure and alignment",
        "concept for a platform that connects local chefs with foodies",
        "startup idea providing modular housing solutions for urban areas",
        "feature to extract contact information from voice recordings",
        "idea for a smart umbrella that alerts you before it rains",
        "concept for a subscription service for eco friendly home products",
        "startup idea offering personalized skincare based on ai analysis",
        "feature to create automated podcasts from a collection of notes",
        "idea for a smart pet feeder that monitors health and weight",
        "concept for a platform for peer to peer car sharing in cities",
        "startup idea providing innovative solutions for vertical farming",
        "feature to search for specific sounds within the audio files"
    ]
    data.extend([(text, 2) for text in idea])

    # REMINDER (80 examples)
    reminder = [
        "dont forget to submit the assignment tonight by midnight",
        "remind me to take medicine after dinner every evening",
        "return library books before friday or pay late fee",
        "remember to water the plants before leaving for trip",
        "call the bank tomorrow morning about the transaction",
        "set alarm for 5am tomorrow important early meeting",
        "need to renew passport before the international trip",
        "follow up on the job application sent last tuesday",
        "dont forget to lock the back door before you go out",
        "pick up the birthday cake from the bakery at 5pm",
        "remember to send the rsvp for the wedding invitation",
        "set a reminder to check the car tire pressure sunday",
        "dont forget to bring the charger for the presentation",
        "remind me to buy a gift for sarahs baby shower tonight",
        "call the landlord about the leaking pipe in bathroom",
        "remember to update the anti virus software on laptop",
        "set an alarm for the 3pm zoom call with the team",
        "dont forget to take the trash out on thursday night",
        "remind me to pick up some milk on the way back home",
        "call the travel agency to confirm the hotel booking",
        "remember to bring the water bottle for the hiking trip",
        "set a reminder to renew the magazine subscription",
        "dont forget to cancel the free trial before it ends",
        "remind me to send the files to the client by eod",
        "call the dentist to reschedule the tuesday appointment",
        "remember to bring the keys for the office tomorrow",
        "set an alarm to start getting ready for the party",
        "dont forget to pay the monthly credit card bill today",
        "remind me to check the oven before leaving the house",
        "call the insurance company about the policy renewal",
        "remember to bring the umbrella it might rain tonight",
        "set a reminder to buy more coffee beans this weekend",
        "dont forget to pack the swimsuit for the holiday",
        "remind me to call the bank about the new debit card",
        "call the internet provider about the slow connection",
        "remember to send the thank you email after the interview",
        "set an alarm for the early morning gym session",
        "dont forget to bring the notebook for the seminar",
        "remind me to buy some fresh flowers for the dinner",
        "call the pharmacy to check if the prescription is ready",
        "remember to update the flight details in the calendar",
        "set a reminder to water the indoor plants tomorrow",
        "dont forget to bring the passport for the check in",
        "remind me to check the mail box for the package",
        "call the car service center to book the maintenance",
        "remember to send the birthday message to aunt mary",
        "set an alarm to take a break from the screen every hour",
        "dont forget to bring the id card for the event tonight",
        "remind me to buy some batteries for the smoke detector",
        "call the support team about the issue with the account",
        "remember to check the fridge for any expired items",
        "set a reminder to call the accountant next monday",
        "dont forget to bring the reusable bags for shopping",
        "remind me to pack the medications for the flight",
        "call the vet to schedule the annual check up for dog",
        "remember to send the quarterly tax estimate by friday",
        "set an alarm for the evening yoga class at 6pm",
        "dont forget to bring the tickets for the concert",
        "remind me to buy some stamps from the post office",
        "call the restaurant to confirm the table reservation",
        "remember to check the pressure of the spare tire",
        "set a reminder to renew the domain name next week",
        "dont forget to bring the presentation slides on usb",
        "remind me to call the electrician for the light fix",
        "call the bank to report the lost credit card immediately",
        "remember to send the updated resume to the recruiter",
        "set an alarm to start the meditation in the morning",
        "dont forget to bring the sun glasses for the drive",
        "remind me to buy some snacks for the long road trip",
        "call the school about the parent teacher meeting",
        "remember to check the oil level in the car engine",
        "set a reminder to buy a new toothbrush next month",
        "dont forget to bring the headphones for the flight",
        "remind me to call the gym about the membership query",
        "call the gas company to report the meter reading",
        "remember to send the wedding gift to the couple",
        "set an alarm for the important client call at 10am",
        "dont forget to bring the map for the remote area",
        "remind me to buy some milk and bread on the way",
        "call the mobile company about the international roaming"
    ]
    data.extend([(text, 3) for text in reminder])

    texts = [item[0] for item in data]
    labels = [item[1] for item in data]
    return texts, labels

def train_model():
    print("STEP 1: Building dataset (320 examples)...")
    texts, labels_raw = get_dataset()
    labels = np.array(labels_raw)

    print("STEP 2: Tokenizing...")
    tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=MAX_LENGTH, padding="post", truncating="post")

    print("STEP 3: One-hot encoding labels...")
    labels_onehot = to_categorical(labels, num_classes=4)

    print("STEP 4: Train/test split (85/15)...")
    X_train, X_test, y_train, y_test = train_test_split(
        padded_sequences, labels_onehot, test_size=0.15, random_state=42, stratify=labels
    )

    print("STEP 5: Building CNN model...")
    model = Sequential([
        Embedding(input_dim=VOCAB_SIZE, output_dim=EMBEDDING_DIM, input_length=MAX_LENGTH),
        Conv1D(filters=256, kernel_size=5, activation="relu"),
        GlobalMaxPooling1D(),
        Dense(128, activation="relu"),
        Dropout(0.4),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(4, activation="softmax")
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
    model.summary()

    print("STEP 6: Training...")
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=4, restore_best_weights=True
    )
    
    # Models directory
    models_dir = os.path.join("app", "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    model_checkpoint_path = os.path.join(models_dir, "cnn_model.keras")
    
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        model_checkpoint_path, monitor="val_accuracy", save_best_only=True, mode="max"
    )

    history = model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=16,
        validation_data=(X_test, y_test),
        callbacks=[early_stop, checkpoint],
        verbose=1
    )

    print("\nSTEP 7: Evaluating...")
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Final Validation Accuracy: {accuracy*100:.2f}%")
    
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)

    target_names = ["work", "personal", "idea", "reminder"]
    print("\nClassification Report:")
    print(classification_report(y_true_classes, y_pred_classes, target_names=target_names))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true_classes, y_pred_classes))

    print(f"\nModel saved to {model_checkpoint_path}")
    
    tokenizer_path = os.path.join(models_dir, "tokenizer.pkl")
    with open(tokenizer_path, "wb") as f:
        pickle.dump(tokenizer, f)
    print(f"Tokenizer saved to {tokenizer_path}")

if __name__ == "__main__":
    train_model()
