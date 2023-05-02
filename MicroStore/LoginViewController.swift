//
//  LoginViewController.swift
//  MicroStore
//
//  Created by Tomer Volloch on 11/04/2023.
//

import UIKit
let sock = SecureSocketManager()
class LoginViewController: UIViewController, UITextFieldDelegate {

    @IBOutlet weak var UsernameTextField: UITextField!
    
    @IBOutlet weak var PasswordTextField: UITextField!
    
    @IBOutlet weak var IpTextField: UITextField!
    
    @IBAction func LoginButton(_ sender: Any) {
        Task {
            do {
                try await sock.connect(host: IpTextField.text!, port: 1233)
                _ = await sock.recv()
                let loggedIn = await sock.login(username: UsernameTextField.text!, password: PasswordTextField.text!)
                if loggedIn == "success" {
                    DispatchQueue.main.async {
                        self.performSegue(withIdentifier: "LoginSegue", sender: self)
                    }
                }
                else {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Login Failed", message: loggedIn, preferredStyle: .alert)
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
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
            self.view.endEditing(true)
            return false
        }

}
