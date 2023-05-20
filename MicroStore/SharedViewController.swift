import UIKit
// This class handles the displaying and interaction with shared files.
class SharedViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView! // Table view to display files
    
    var files: [SharedItem] = [] // Array to store files
        
    // Method to refresh data from the server and reload table view.
    func refreshData() {
        Task {
            let files = await sock.getShared()
            DispatchQueue.main.async {
                self.files = files
                self.tableView.reloadData()
            }
        }
    }

    // Method called when view loads. It sets table view's data source and delegate.
    override func viewDidLoad() {
        super.viewDidLoad()
                
        tableView.dataSource = self
        tableView.delegate = self
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshData()
    }
}

// Extension to conform to UITableViewDataSource and UITableViewDelegate protocols
extension SharedViewController : UITableViewDataSource, UITableViewDelegate {
    
    // Returns the number of files.
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return files.count
    }
    
    // Sets up each cell with the appropriate file's data.
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell =  tableView.dequeueReusableCell(withIdentifier: "fileCell", for: indexPath)
        cell.textLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)
        cell.detailTextLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)

        cell.textLabel?.text = files[indexPath.row].name
        cell.detailTextLabel?.text = files[indexPath.row].perm
        return cell
    }
    
    // Defines actions upon selecting a file from the table.
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        let itemName = files[indexPath.row].name
        let itemID = files[indexPath.row].uuid
        
        let actionSheet = UIAlertController(title: nil, message: "Choose an action for \(itemName)", preferredStyle: .actionSheet)
        
        
        let downloadAction = UIAlertAction(title: "Download", style: .default) { _ in
            Task {
                let (result, fileData) = await sock.download(path: "|" + itemID)
                if result == itemName, let data = fileData {
                    DispatchQueue.main.async {
                        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(itemName)
                        do {
                            try data.write(to: tempURL)
                            let activityViewController = UIActivityViewController(activityItems: [tempURL], applicationActivities: nil)
                            self.present(activityViewController, animated: true, completion: nil)
                        } catch {
                            let alertController = UIAlertController(title: "Error", message: "Failed to save the file locally.", preferredStyle: .alert)
                            alertController.addAction(UIAlertAction(title: "OK", style: .default))
                            self.present(alertController, animated: true)
                        }
                    }
                } else {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                }
            }
            
        }
        
        let shareAction = UIAlertAction(title: "Share", style: .default) { _ in
            let alertController = UIAlertController(title: "Share File", message: "Enter the username and choose the permission level.", preferredStyle: .alert)
            
            alertController.addTextField { textField in
                textField.placeholder = "Username"
            }
            
            alertController.addAction(UIAlertAction(title: "Share", style: .default) { _ in
                guard let username = alertController.textFields?.first?.text, !username.isEmpty else {
                    return
                }
                
                let permissionActionSheet = UIAlertController(title: "Choose Permission", message: nil, preferredStyle: .actionSheet)
                
                for permission in ["viewer", "editor"] {
                    permissionActionSheet.addAction(UIAlertAction(title: permission, style: .default) { _ in
                        Task { let result = await sock.share(name: username, path: "|"+itemID, perm: permission)
                            if result != "success" {
                                DispatchQueue.main.async {
                                    let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                                    alertController.addAction(UIAlertAction(title: "OK", style: .default))
                                    self.present(alertController, animated: true)
                                }
                                return
                            }
                        }
                    })
                }
                
                permissionActionSheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
                
                self.present(permissionActionSheet, animated: true)
            })
            
            alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            
            self.present(alertController, animated: true)
        }
        

        let removeAction = UIAlertAction(title: "Remove", style: .default) { _ in
            Task { let result = await sock.remove(path: "|" + itemID)
                if result != "success" {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                    return
                }
                self.refreshData()
            }
        }
        
        let copyAction = UIAlertAction(title: "Copy", style: .default) { _ in
            copyName = itemName
            cutName = ""
            sourceID = itemID
        }
        
        let cutAction = UIAlertAction(title: "Cut", style: .default) { _ in
            cutName = itemName
            copyName = ""
            sourceID = itemID
        }
        
        let changeNameAction = UIAlertAction(title: "Rename", style: .default) { _ in
            let alertController = UIAlertController(title: "Share File", message: "Enter the username and choose the permission level.", preferredStyle: .alert)
            
            alertController.addTextField { textField in
                textField.text = itemName
                textField.placeholder = "New name"
            }
            
            alertController.addAction(UIAlertAction(title: "Rename", style: .default) { _ in
                guard let newName = alertController.textFields?.first?.text, !newName.isEmpty else {
                    return
                }
                Task { let result = await sock.rename(oldName: "|"+itemID, newName: newName)
                    if result != "success" {
                        DispatchQueue.main.async {
                            let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                            alertController.addAction(UIAlertAction(title: "OK", style: .default))
                            self.present(alertController, animated: true)
                        }
                        return
                    }
                    self.refreshData()
                }
                
            })
            
            alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            
            self.present(alertController, animated: true)
        }
        
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel, handler: nil)
        
        actionSheet.addAction(downloadAction)
        actionSheet.addAction(shareAction)
        actionSheet.addAction(removeAction)
        actionSheet.addAction(copyAction)
        actionSheet.addAction(cutAction)
        actionSheet.addAction(changeNameAction)
        actionSheet.addAction(cancelAction)
        
        tableView.deselectRow(at: indexPath, animated: true)
        self.present(actionSheet, animated: true, completion: nil)
    }
}

// Struct representing a shared file.
struct SharedItem {
    let name: String // Name of the file
    let perm: String // Permission status of the file
    let uuid: String // Unique identifier of the file
}
