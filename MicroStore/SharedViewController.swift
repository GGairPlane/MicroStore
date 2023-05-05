//
//  SharedViewController.swift
//  MicroStore
//
//  Created by Tomer Volloch on 25/04/2023.
//

import UIKit

class SharedViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    
    var dirs: [SharedItem] = []
    var files: [SharedItem] = []
        
    
    func refreshData() {
        Task {
            let (dirs, files) = await sock.getShared()
            DispatchQueue.main.async {
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }

    
    override func viewDidLoad() {
        super.viewDidLoad()
                
        tableView.dataSource = self
        tableView.delegate = self
        
        refreshData()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshData()
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}

extension SharedViewController : UITableViewDataSource, UITableViewDelegate {
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return files.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell =  tableView.dequeueReusableCell(withIdentifier: "fileCell", for: indexPath)
        cell.textLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)
        cell.detailTextLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)

        cell.textLabel?.text = files[indexPath.row].name
        cell.detailTextLabel?.text = files[indexPath.row].perm
        return cell
    }
    
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        let itemName = files[indexPath.row].name
        
        let actionSheet = UIAlertController(title: nil, message: "Choose an action for \(itemName)", preferredStyle: .actionSheet)
        
        
        let downloadAction = UIAlertAction(title: "Download", style: .default) { _ in
            Task {
                let (result, fileData) = await sock.download(path: "|" + itemName)
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
                
                for permission in ["Viewer", "Editor"] {
                    permissionActionSheet.addAction(UIAlertAction(title: permission, style: .default) { _ in
                        Task { let result = await sock.share(name: username, path: "|"+itemName, perm: permission)
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
            Task { let result = await sock.remove(path: "|" + itemName)
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
            toCopy = "|" + itemName
            toCut = ""
        }
        
        let cutAction = UIAlertAction(title: "Cut", style: .default) { _ in
            toCut = "|" + itemName
            toCopy = ""
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
                Task { let result = await sock.rename(oldName: "|"+itemName, newName: "|"+newName)
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


struct SharedItem {
    let name: String
    let perm: String
    let uuid: String
    
}
