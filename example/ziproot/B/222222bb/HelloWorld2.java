/**
 * A class for keeping the hello world message.
 *
 * @author Tommi Tervonen (1911667) and his Alter Ego (6671911)
 */
public class HelloWorld2 {

	private static final String MESSAGE = "Hello World!";
	private String message;

	/**
	 * Constructs a new hello world with the default message.
	 */
	public HelloWorld2() {
		this.message = MESSAGE;
	}

	/**
	 * Gets the currently set message.
	 *
	 * @return the current message
	 */
	public String getMessage() {
		return message;
	}

	/**
	 * Sets the message.
	 *
	 * @param newMsg the new message
	 */
	public void setMessage(String newMsg) {
		message = newMsg;
	}
}