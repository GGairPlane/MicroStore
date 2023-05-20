
import UIKit
let sock = SecureSocketManager.shared

// This class handles the login and sign up process.
class LoginViewController: UIViewController, UITextFieldDelegate {

    // UITextField for entering username
    @IBOutlet weak var UsernameTextField: UITextField!
    
    // UITextField for entering password
    @IBOutlet weak var PasswordTextField: UITextField!
    
    // UITextField for entering IP address of the server
    @IBOutlet weak var IpTextField: UITextField!
    
    // This method is triggered when the login button is clicked. it handles login procedure
    @IBAction func LoginButton(_ sender: Any) {
        Task {
            do {
                // Connect to the server
                try await sock.connect(host: IpTextField.text!, port: 1233)
                // Receive initial server message
                _ = await sock.recv()
                // Send login credentials to the server
                let loggedIn = await sock.login(username: UsernameTextField.text!, password: PasswordTextField.text!)
                // Check login status
                if loggedIn == "success" {
                    // Update UI on the main thread
                    DispatchQueue.main.async {
                        // Perform segue to the next view controller on successful login
                        self.performSegue(withIdentifier: "LoginSegue", sender: self)
                    }
                }
                else {
                    // Update UI on the main thread
                    DispatchQueue.main.async {
                        // Show alert with the server's response on failed login
                        let alertController = UIAlertController(title: "Login Failed", message: loggedIn, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                }
            } catch {
                // Update UI on the main thread
                DispatchQueue.main.async {
                    // Show alert if connection to the server cannot be established
                    let alertController = UIAlertController(title: "Connection Error", message: "Unable to connect to the server.", preferredStyle: .alert)
                    alertController.addAction(UIAlertAction(title: "OK", style: .default))
                    self.present(alertController, animated: true)
                }
            }
        }
    }
    
    // Similar to the login function, but this one handles new user registration.
    @IBAction func SignUpButton(_ sender: Any) {
        Task {
            do {
                try await sock.connect(host: IpTextField.text!, port: 1233)
                _ = await sock.recv()
                let loggedIn = await sock.signup(username: UsernameTextField.text!, password: PasswordTextField.text!)
                if loggedIn == "success" {
                    DispatchQueue.main.async {
                        self.performSegue(withIdentifier: "LoginSegue", sender: self)
                    }
                }
                else {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Signup Failed", message: loggedIn, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    let alertController = UIAlertController(title: "Connection Error", message: "Unable to connect to the server.", preferredStyle: .alert)
                    alertController.addAction(UIAlertAction(title: "OK", style: .default))
                    self.present(alertController, animated: true)
                }
            }
        }
    }
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.UsernameTextField.delegate = self
        self.PasswordTextField.delegate = self
        self.IpTextField.delegate = self

        
    }
    


    // This method is called when the return button is pressed on the keyboard.
    // It dismisses the keyboard.
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
            self.view.endEditing(true)
            return false
        }

}
